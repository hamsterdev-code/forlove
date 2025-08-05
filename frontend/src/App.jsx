import { useState } from 'react'
import UsersTable from "./components/UsersTable";
import PaysTable from './components/PaysTable';
import TransfersTable from './components/TransfersTable';

function App() {
  const [page, setPage] = useState("users");

  return (
    <>
      {page === "users" && <UsersTable setPage={setPage} />}
      {page === "pays" && <PaysTable setPage={setPage} />}
      {page === "transfers" && <TransfersTable setPage={setPage} />}
    </>
  );
}

export default App
