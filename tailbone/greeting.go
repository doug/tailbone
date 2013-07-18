package tailbone

import (
	"appengine/datastore"
	"github.com/crhym3/go-endpoints/endpoints"
	"net/http"
	"time"
)

// Greeting is a datastore entity that represents a single greeting.
// It also serves as (a part of) a response of GreetingService.
type Greeting struct {
	Key     *datastore.Key `json:"id" datastore:"-"`
	Author  string         `json:"author"`
	Content string         `json:"content" datastore:",noindex" endpoints:"req"`
	Date    time.Time      `json:"date"`
}

// GreetingsList is a response type of GreetingService.List method
type GreetingsList struct {
	Items []*Greeting `json:"items"`
}

// Request type for GreetingService.List
type GreetingsListReq struct {
	Limit int `json:"limit" endpoints:"d=10"`
}

// GreetingService can sign the guesbook, list all greetings and delete
// a greeting from the guestbook.
type GreetingService struct {
}

// List responds with a list of all greetings ordered by Date field.
// Most recent greets come first.
func (gs *GreetingService) List(
	r *http.Request, req *GreetingsListReq, resp *GreetingsList) error {

	if req.Limit <= 0 {
		req.Limit = 10
	}

	c := endpoints.NewContext(r)
	q := datastore.NewQuery("Greeting").Order("-Date").Limit(req.Limit)
	greets := make([]*Greeting, 0, req.Limit)
	keys, err := q.GetAll(c, &greets)
	if err != nil {
		return err
	}

	for i, k := range keys {
		greets[i].Key = k
	}
	resp.Items = greets
	return nil
}

func init() {
	greetService := &GreetingService{}
	api, err := endpoints.RegisterService(greetService,
		"greeting", "v1", "Greetings API", true)
	if err != nil {
		panic(err.Error())
	}

	info := api.MethodByName("List").Info()
	info.Name, info.HttpMethod, info.Path, info.Desc = 
		"greets.list", "GET", "greetings", "List most recent greetings."

	// endpoints.HandleHttp()
}
