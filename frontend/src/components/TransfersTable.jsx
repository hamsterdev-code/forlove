// TransfersTable.jsx
import React, { useEffect, useState } from "react";
import { payFields } from "../data/payFields";
import "./../styles/style.css";
import axios from "axios"
import { BASE_URL } from "../constants";
import { transferFields } from "../data/transferFields";
const fetchTransfersList = async () => {
    let { data } = await axios.get(`${BASE_URL}/admin/transfers`)
    return data
};

const TransfersTable = ({ setPage }) => {
    const [loading, setLoading] = useState(true)
    const [transfers, setTransfers] = useState([]);

    useEffect(() => {
        (async () => {
            const data = await fetchTransfersList();
            setTransfers(data);
            setLoading(false)
        })()
    }, []);

    return (
        <div className="admin-wrapper">
            <aside className="sidebar">
            <h2 className="title">Гл. Админка</h2>
                <ul>
                    <li onClick={() => { setPage("users") }}>Пользователи</li>
                    <li onClick={() => { setPage("pays") }}>Транзакции</li>
                    <li className="active">Переводы</li>
                </ul>
            </aside>
            <main className="content">
                {loading ? (<h3 className="loading_text">Загрузка...</h3>) : (
                    <>
                        <div className="content-header">
                            <h2>Переводы</h2>
                        </div>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th><input type="checkbox" /></th>
                                        <th></th>
                                        {transferFields.map(f => (
                                            <th key={f.key}>{f.label}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {transfers.map(user => (
                                        <tr key={user.id}>
                                            <td><input type="checkbox" /></td>
                                            <td className="icon-cell">
                                            </td>
                                            {transferFields.map(f => (
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

export default TransfersTable;
