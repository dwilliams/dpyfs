import {EventAggregator} from 'aurelia-event-aggregator';
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';

// @inject(WebAPI, EventAggregator)
// export class ContactList {
  // contacts;
  // selectedId = 0;
// 
  // constructor(private api: WebAPI, ea: EventAggregator) {
    // ea.subscribe(ContactViewed, msg => this.select(msg.contact));
    // ea.subscribe(ContactUpdated, msg => {
      // let id = msg.contact.id;
      // let found = this.contacts.find(x => x.id == id);
      // Object.assign(found, msg.contact);
    // });
  // }
// 
  // created() {
    // this.api.getContactList().then(contacts => this.contacts = contacts);
  // }
// 
  // select(contact) {
    // this.selectedId = contact.id;
    // return true;
  // }
// }


// @inject(HttpClient)
// export class FileList {
// 
    // constructor(http) {
        // this.http = http;
    // }
// 
    // getSomeJson() {
        // this.http.fetch('something')
            // .then(response => response.json())
            // .then(data => {
                    // console.log(data);
            // })
    // }
// 
//}

let httpClient = new HttpClient();

httpClient.configure(config => {
  config
    .withBaseUrl('/')
    .withDefaults({
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'Fetch'
      }
    })
    .withInterceptor({
      request(request) {
        console.log(`Requesting ${request.method} ${request.url}`);
        return request;
      },
      response(response) {
        console.log(`Received ${response.status} ${response.url}`);
        return response;
      }
    });
});

httpClient.fetch('download/')
  .then(response => response.json())
  .then(data => {
    console.log(data.description);
});