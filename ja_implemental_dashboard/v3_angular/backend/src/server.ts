import http from 'http';
import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';

// Open a database connection
async function openDb() {
  return open({
    filename: './example_data/database.sqlite3',
    driver: sqlite3.Database
  });
}

// Function to get table names
async function getTableNamesList(db: Database): Promise<string[]> {
  try {
    const rows = await db.all<{ name: string }[]>('SELECT name FROM sqlite_master WHERE type=\'table\';');
    return rows.map(row => row.name);
  } catch (err) {
    console.error('Error executing SQL query:', err);
    throw err;
  }
}

// Create and start the server
const server = http.createServer(async (req, res) => {
  const start_time = Date.now();
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  // response has a body property that is a stringified JSON object
  // response has a bodyStatusCode property that is the status code of the body response
  // If request has nothing, return a simple message
  if (!req.url || req.url === '/') {
    res.end(JSON.stringify({ 'body': 'Hello, World!', 'bodyStatusCode': 200 }));
    return;
  }
  // If GET request has request=table_names, get the table names from the database
  if (req.url?.includes('request=table_names')) {
    try {
      const db = await openDb();
      const table_names = await getTableNamesList(db);
      await db.close();
      res.end(JSON.stringify({ 'body': table_names, 'bodyStatusCode': 200 }));
      return;
    } catch (err) {
      console.error(`Error fetching table names: ${err}`);
      res.end(JSON.stringify({ 'body': 'Error fetching table names', 'bodyStatusCode': 500 }));
      return;
    }
  }
  // If request is not recognized, return a simple message
  res.end(JSON.stringify({ body: 'Request not recognized', bodyStatusCode: 404 }));
});

// server.listen(3000, () => {
//   let string_ = "";
//   string_ += "Server running at http://localhost:3000/";
//   string_ += "\nUse Ctrl-C to stop the server";
//   console.log(string_);
// });

const server_address = '192.168.0.54'; // 'localhost';
const server_port = 3000;

server.listen(server_port, server_address, () => {
  let string_ = "";
  string_ += "Server running at http://"+server_address+":"+server_port+"/";
  string_ += "\nUse Ctrl-C to stop the server";
  console.log(string_);
});