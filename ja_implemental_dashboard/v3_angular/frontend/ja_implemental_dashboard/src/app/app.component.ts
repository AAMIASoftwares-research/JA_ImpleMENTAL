import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

const server_url = 'http://localhost:3000/';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'ja_implemental_dashboard';

  callServer() {
    const serverResponseElement = document.getElementById('server_response');
    fetch(server_url+'?request=table_names', )
      .then(response => response.json())
      .then(data => {
        if (serverResponseElement) {
          console.log('Data fetched from server:', data);
          serverResponseElement.innerText = data.body;
        }
      })
      .catch(error => {
        console.error('Error fetching data from server:', error);
        if (serverResponseElement) {
          serverResponseElement.innerText = 'Error fetching data from server';
          serverResponseElement.style.color = 'red';
        }
      });
  }
}
