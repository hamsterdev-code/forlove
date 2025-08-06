// UsersTable.jsx
import React, { useEffect, useState } from "react";
import { userFields } from "../data/userFields";
import "./../styles/style.css";
import axios from "axios"
import { BASE_URL } from "../constants";
const fetchUsersList = async () => {
  let { data } = await axios.get(`${BASE_URL}/admin/users`)
  return data
};

const UsersTable = ({ setPage }) => {
  const [loading, setLoading] = useState(true)
  const [users, setUsers] = useState([]);

  useEffect(() => {
    (async () => {
      const data = await fetchUsersList();
      setUsers(data);
      setLoading(false)
    })()
  }, []);

  return (
    <div className="admin-wrapper">
      <aside className="sidebar">
        <h2 className="title">Гл. Админка</h2>
        <ul>
          <li className="active">Пользователи</li>
          <li onClick={() => { setPage("pays") }}>Транзакции</li>
          <li onClick={() => { setPage("transfers") }}>Переводы</li>
        </ul>
      </aside>
      <main className="content">
        {loading ? (<h3 className="loading_text">Загрузка...</h3>) : (
          <>
            <div className="content-header">
              <h2>Пользователи</h2>
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th><input type="checkbox" /></th>
                    <th></th>
                    {userFields.map(f => (
                      <th key={f.key}>{f.label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td><input type="checkbox" /></td>
                      <td className="icon-cell">
                      </td>
                      {userFields.map(f => (
                        <td key={f.key}>{user[f.key]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

      </main>
    </div>
  );
};

export default UsersTable;
