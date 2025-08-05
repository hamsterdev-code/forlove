import { useState } from 'react'
import UsersTable from "./components/UsersTable";
import PaysTable from './components/PaysTable';

function App() {
  const [page, setPage] = useState("users");

  return (
    <>
      {page === "users" && <UsersTable setPage={setPage} />}
      {page === "pays" && <PaysTable setPage={setPage} />}
    </>
  );
}

export default App
