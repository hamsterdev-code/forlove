import { useEffect, useState } from "react";
import { BASE_URL } from "./constants";
import axios from "axios";

export default function Modal({ username, onClose }) {
  if (!username) return null;
  const [userData, setUserData] = useState({purchases: []})

  useEffect(() => {
    (async () => {
      let { data } = await axios.get(`${BASE_URL}/users/${username}/data`)
      setUserData(data)
      console.log(data);
    })()
  }, [])

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#fff",
          padding: "20px 30px",
          borderRadius: 10,
          boxShadow: "0 4px 15px rgba(0,0,0,0.4)",
          minWidth: 250,
          animation: "fadeIn 0.2s ease-out",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>Информация</h3>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Имя:</strong> {userData.name}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Ник ТГ:</strong> {username}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Город:</strong> {userData.city}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Баланс:</strong> {userData.balance}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Внутренний баланс:</strong> {userData.inner_balance}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Людей в 1 линии:</strong> {userData["1_line_refs"]}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Людей в структуре:</strong> {userData.line_refs}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Сумма покупок:</strong> {userData.total_pays}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Спонсор:</strong> {userData.ref}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Оборот стркутуры:</strong> {userData.total_structure_buys}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Дата рег.:</strong> {userData.reg_date}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Дата последней покупки:</strong> {userData.last_pay}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Уровень пакета:</strong> {{1: "Обычный", 2: "Любитель", 3: "Профессионал", 4: "Наставник", 5: "Куратор", 6: "Амбассадор"}[userData.ref_level]}</p>
        <p style={{ margin: 0, fontSize: 16, }}><strong>Покупки:</strong>
          <select name="pets" id="pet-select">
            {userData.purchases.map((v)=>(
              <option value={v}>{v}</option>
            ))}
          </select>
        </p>
        <button
          onClick={onClose}
          style={{
            marginTop: 15,
            padding: "6px 12px",
            background: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          Закрыть
        </button>
      </div>
    </div>
  );
};