/**
 * @author Doug Fritz dougfritz@google.com
 * @author Maciej Zasada maciej@unit9.com
 * Date: 6/2/13
 * Time: 10:53 PM
 */

/**
 * Internal Mesh utility functions
 * @type {{addNodes: Function, removeNodes: Function, restGet: Function}}
 */
var MeshUtils = {

    uidSeed: 1,

    /**
     * Adds remote nodes to Mesh.peers
     * @param mesh {Mesh}
     * @param nodes {array(string)}
     */
    addNodes: function (mesh, nodes) {

        var i, node;

        for (i = 0; i < nodes.length; ++i) {

            node = nodes[i];
            mesh.peers.push(node);

            if (mesh.options.autoPeerConnect) {

                node.connect();

            }

        }

    },

    /**
     * Removes remote nodes from Mesh.peers
     * @param mesh {Mesh}
     * @param nodes {array(string)}
     */
    removeNodes: function (mesh, nodes) {

        var i, node;

        for (i = 0; i < nodes.length; ++i) {

            node = nodes[i];
            node.disconnect();
            mesh.peers.splice(mesh.peers.indexOf(node), 1);

        }

    },

    /**
     * Executes an asynchronous HTTP GET request
     * @param url {string}
     * @param successHandler {function}
     * @param failureHandler {function}
     */
    restGet: function (url, successHandler, failureHandler) {

        var xmlhttp;

        if (window.XMLHttpRequest) {

            xmlhttp = new XMLHttpRequest();

        } else {

            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");

        }

        xmlhttp.onreadystatechange = function () {

            if (xmlhttp.readyState === 4) {

                if (xmlhttp.status === 200 && typeof successHandler === 'function') {

                    successHandler(xmlhttp.responseText);

                } else {

                    failureHandler(xmlhttp.status);

                }

            }

        };

        xmlhttp.open('GET', url, true);
        xmlhttp.send();

    }

};

/**
 * Mesh
 * @param id {string} ID of Mesh to join or create, or undefined to create new Mesh and generate ID
 * @param options {string|object} string URL of load balancer API or actual config object
 * @constructor
 */
var Mesh = function (id, options) {

    var self = this;

    StateDrive.call(this);

    if (id && typeof id !== 'string') {

        throw new Error('Invalid type ID');

    }

    var uid = MeshUtils.uidSeed++;
    this.__defineGetter__('uid', function () {
        return uid;
    });

    this.id = id;
    this.self = new Node(this, null);
    this.peers = [];
    ['bind', 'unbind', 'trigger'].forEach(function(name) {
        self.peers[name] = function() {
            var originalArguments = arguments;
            self.peers.forEach(function (peer) {
                peer[name].apply(peer, originalArguments);
            });
        }
    });

    this.options = {};

    this.config(options);
    this.setState(Mesh.STATE.INITIALISED);
    this.setMinCallState('connect', Mesh.STATE.INITIALISED);

    this.self.bind('exist', function () {

        MeshUtils.addNodes(self, arguments);

    });

    this.self.bind('enter', function () {

        MeshUtils.addNodes(self, arguments);

    });

    this.self.bind('leave', function () {

        MeshUtils.removeNodes(self, arguments);

    });

    if (this.options.autoConnect) {

        this.connect();

    }

};

/**
 * Extend StateDrive
 * @type {StateDrive}
 */
Mesh.prototype = new StateDrive();

/**
 * Returns unique Mesh string representation.
 * Essential to make dictionary indexing by Node work.
 * @returns {string}
 */
Mesh.prototype.toString = function () {

    return 'Mesh@' + this.uid;

};

/**
 * Configures mesh
 * @param options {string|object} string URL of load balancer API or actual config object
 */
Mesh.prototype.config = function (options) {

    var field;

    for (field in Mesh.options) {

        this.options[field] = this.options[field] === undefined ? Mesh.options[field] : this.options[field];

    }

    if (typeof options === 'string') {

        this.options.api = options;

    } else if (typeof options === 'object') {

        for (field in options) {

            this.options[field] = options[field];

        }

    }

};

/**
 * Connects self Node to the mesh.
 * If WebSocket IP is specified, attempts direct connection.
 * Otherwise, attempts to retrieve config object from load balancer via its API url.
 */
Mesh.prototype.connect = function () {

    var self = this,
        options,
        idMatch;

    if (this.options.ws) {

        idMatch = this.options.ws.match('[^\/]+$');
        if (idMatch) {

            this.id = idMatch[0];

        }

        this.self.connect();

        this.peers.forEach(function (peer) {

            peer.connect();

        });

    } else if (this.options.api) {

        MeshUtils.restGet(this.options.api + '/' + (this.id || ''), function (response) {

            try {

                var options = JSON.parse(response);
                self.config(options);
                self.connect();

            } catch (e) {

                throw new Error('Could not establish connection with server');

            }

        }, function () {

            console.warn("Error connecting to server, retrying in 10 seconds.");
            setTimeout(function() {
                self.connect();
            }, 10*1000);

            // throw new Error('Could not establish connection with server');

        });

    } else {

        throw new Error('Invalid options');

    }

};

/**
 * Disconnects all Nodes
 */
Mesh.prototype.disconnect = function () {

    this.self.disconnect();

    this.peers.forEach(function (peer) {

        peer.disconnect();

    });

};

/**
 * Binds event
 * @param type
 * @param handler
 */
Mesh.prototype.bind = function (type, handler) {

    this.self.bind.apply(this.self, arguments);

    this.peers.bind.apply(this, arguments);

};

/**
 * Unbinds event
 * @param type
 * @param handler
 */
Mesh.prototype.unbind = function (type, handler) {

    this.self.unbind.apply(this.self, arguments);

    this.peers.unbind.apply(this, arguments);

};

/**
 * Triggers event
 * @param type
 * @param args
 */
Mesh.prototype.trigger = function (type, args) {

    this.self.trigger.apply(this.self, arguments);

    this.peers.trigger.apply(this, arguments);

};

/**
 * Supported Mesh StateDrive states
 * @type {{INVALID: number, UNDEFINED: number, INITIALISED: number, CONNECTED: number}}
 */
Mesh.STATE = {

    INVALID: -1,
    UNDEFINED: 0,
    INITIALISED: 1,
    CONNECTED: 2

};

/**
 * Common Mesh options
 * @type {{api: '/api/mesh', autoConnect: boolean}}
 */
Mesh.options = {

    api: '/api/mesh',
    autoConnect: false,
    autoPeerConnect: true

};
