# JA ImpleMENTAL Dashboard


## Technical Overview

This version of the Dashboard follows the best prctice of creating a Model-View-Controller (MVC) architecture. 
The MVC architecture is a software design pattern that separates the application into three main components: the Model, the View, and the Controller.
The Model is responsible for managing the data of the application. It receives user input from the Controller, processes it, and sends the data to the View.
The View is responsible for displaying the data to the user. It receives data from the Model and presents it to the user in a format that is easy to understand.
The Controller is responsible for handling user input and updating the Model and View accordingly. It receives input from the user, processes it, and sends the data to the Model. The Model then processes the data and sends it to the View for display. 
The Dashboard follows this architecture to ensure that it is well-structured and easy to maintain.

## MVC Architecture and Server Interaction

This application is designed to only run locally. It does not need internet. However, it is also designed to be extendible to a server-client architecture, where the server is another machine somewhen in the internet (for example, a cloud server).

- Client: The client is the user's computer. It runs the Dashboard application and interacts with the server to get data.
    - The client is responsible for displaying the data to the user. It receives data from the server and presents it to the user in a format that is easy to understand. It holds all the interactivity of the application and the user interface.
    - The client uses Angular to build the UI and handle the interactions with the user.
    - The client uses D3.js, Chart.js or Bokeh.js to build the charts and graphs that display the data, and handle interactivity.
    - Where possible, everything is coded in TypeScript at developement time, and then compiled to JavaScript of course.
- Server: The server is a machine that hosts the data and serves it to the client. In this case, it is the same as the client, which runs a node.js server. It is responsible for handling requests from the client and sending data back to the client. Specifically:
    - The server holds a SQLite database with the data. The server is responsible of running SQL queries to get the data from the database.
    - The server runs a node.js server that listens for requests from the client. The server processes the requests and sends the data back to the client. Requests are of type "STANDARD" or "DEBUG".
        - STANDARD is a request that is already implemented in the server. All production usecases only use STANDARD requests.
        - DEBUG is a request that is not implemented in the server. It is used for development purposes only, and requires a passkey PASSKEY to be sent along with the request. The server will only respond to DEBUG requests if the passkey is correct.
    The server sends back the data in pure JSON format.

If i have the UI, the js that builds and changes the UI and defines the callbacks, and the server that sends the data, then i have the MVC architecture thus structured:
- The UI is the View
- The js that builds and changes the UI and defines the callbacks is the Controller
- The server that sends the data is the Model

## Installation (Development)

The installation and running process should be as easy and hassle-free for the user as possible. The user should be able to run the Dashboard just by opening the browser and going into the (local) URL where the Dashboard is hosted. The user should not have to install any dependencies or run any commands in the terminal.

The Dashboard dependencies are for developing are:
- Frontend-side (View and Controller):
    - Node.js to install Angular CLI 18 (or higher) 
    - Angular
    - D3.js
    - Chart.js
    - Bokeh.js
- Backend-side (Model in the server):
    - Node.js tu run the HTTP server
    - SQLite

``` bash
npm install --save-dev typescript ts-node nodemon @types/node
# setup the ./tsconfig.json file
# setup the ./package.json file with the nodemon script
# run the server with nodemon by running `npm run dev` in the terminal

```

## Installation (Production)

Users of the dashboard are provided with the compiled version of the Dashboard frontend, so they can just open it in the browser and start using it. Regarding the backend, the user is provided with a node.js server that runs the SQLite database and listens for requests from the client. The server is installed automatically when the user installs the Dashboard frontend, and the server is started automatically when the user opens the Dashboard frontend in the browser.

To achieve this, the Dashboard is compiled to a single HTML file, a single CSS file, and a single JS file. The JS file contains all the Angular, D3.js, Chart.js, and Bokeh.js code. The CSS file contains all the CSS code. The HTML file contains the structure of the page and the references to the CSS and JS files. The user only needs to open the HTML file in the browser to start using the Dashboard. To install the server, the user only needs to run the server executable, which is provided along with the Dashboard frontend. Specifically, the user is provided an installer file that installs the server and the frontend in the user's computer. The installer file is a single executable file that the user can run to install the Dashboard.