// PaysTable.jsx
import React, { useEffect, useState } from "react";
import { payFields } from "../data/payFields";
import "./../styles/style.css";
import axios from "axios"
import { BASE_URL } from "../constants";
const fetchPaysList = async () => {
    let { data } = await axios.get(`${BASE_URL}/admin/pays`)
    return data
};

const PaysTable = ({ setPage }) => {
    const [loading, setLoading] = useState(true)
    const [pays, setPays] = useState([]);

    useEffect(() => {
        (async () => {
            const data = await fetchPaysList();
            setPays(data);
            setLoading(false)
        })()
    }, []);

    return (
        <div className="admin-wrapper">
            <aside className="sidebar">
                <h2 className="title">Гл. Админка</h2>
                <ul>
                    <li onClick={() => { setPage("users") }}>Пользователи</li>
                    <li className="active">Транзакции</li>
                    <li onClick={() => { setPage("transfers") }}>Переводы</li>
                </ul>
            </aside>
            <main className="content">
                {loading ? (<h3 className="loading_text">Загрузка...</h3>) : (
                    <>
                        <div className="content-header">
                            <h2>Транзакции</h2>
                        </div>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th><input type="checkbox" /></th>
                                        <th></th>
                                        {payFields.map(f => (
                                            <th key={f.key}>{f.label}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {pays.map(user => (
                                        <tr key={user.id}>
                                            <td><input type="checkbox" /></td>
                                            <td className="icon-cell">
                                            </td>
                                            {payFields.map(f => (
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

export default PaysTable;
