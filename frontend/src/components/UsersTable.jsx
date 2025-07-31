// UsersTable.jsx
import React, { useEffect, useState } from "react";
import { userFields } from "../data/userFields";
import "./../styles/style.css";

const fetchUsersList = () => {
  return Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    role: i % 2 === 0 ? "Admin" : "User",
    status: i % 3 === 0 ? "Active" : "Inactive"
  }));
};

const UsersTable = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const data = fetchUsersList();
    setUsers(data);
  }, []);

  return (
    <div className="admin-wrapper">
      <aside className="sidebar">
        <h2>Admin</h2>
        <ul>
          <li className="active">Users</li>
          <li>Addresses</li>
          <li>Profiles</li>
        </ul>
      </aside>
      <main className="content">
        <div className="content-header">
          <h3>Users</h3>
        </div>
        <div className="actions-bar">
          <button className="dropdown-btn">Actions ▼</button>
          <input type="text" placeholder="Search: name" className="search-input" />
          <button className="search-btn">Search</button>
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
                    <span className="icon">👁</span>
                    <span className="icon">✏️</span>
                    <span className="icon">📋</span>
                    <span className="icon">🗑</span>
                  </td>
                  {userFields.map(f => (
                    <td key={f.key}>{user[f.key]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pagination">
          <span>Showing 1 to 10 of 100 items</span>
          <div className="pagination-controls">
            <span className="disabled">‹ prev</span>
            {[1, 2, 3, 4].map(p => (
              <span key={p} className={p === 1 ? "active" : ""}>{p}</span>
            ))}
            <span>next ›</span>
            <select>
              <option>10 / Page</option>
            </select>
          </div>
        </div>
      </main>
    </div>
  );
};

export default UsersTable;
