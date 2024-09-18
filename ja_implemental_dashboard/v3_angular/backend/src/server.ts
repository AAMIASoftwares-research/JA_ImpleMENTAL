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
    console.log('Rows fetched from database:', rows); // Debugging log
    return rows.map(row => row.name);
  } catch (err) {
    console.error('Error executing SQL query:', err);
    throw err;
  }
}

// Create and start the server
const server = http.createServer(async (req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/html');
  let out = 'Hello, world! This is a new server!br>';
  out += `Request: ${req.url}<br>`;
  // If GET request has request=table_names, get the table names from the database
  if (req.url?.includes('request=table_names')) {
    try {
      const db = await openDb();
      const table_names = await getTableNamesList(db);
      out += `Table names: ${table_names.join(', ')}<br>`;
    } catch (err) {
      console.error(`Error fetching table names: ${err}`);
      out += `Error fetching table names: ${err}<br>`;
    }
  }
  res.end(out);
});

server.listen(3000, () => {
  let string_ = "";
  string_ += "Server running at http://localhost:3000/";
  string_ += "\nUse Ctrl-C to stop the server";
  string_ += "\nUse a GET request like ?request=table_names to get the table names from the database";
  console.log(string_);
});