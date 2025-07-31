import { useState } from 'react'
import UsersTable from "./components/UsersTable";

function App() {
  const [page, setPage] = useState("users");

  return (
    <>
      {page === "users" && <UsersTable />}
      <div style={{ position: "fixed", bottom: 10, left: 10 }}>
        <button onClick={() => setPage("users")}>Users</button>
      </div>
    </>
  );
}

export default App
