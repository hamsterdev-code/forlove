import React, { useState } from 'react';
import UserTree from './UserTree';

function App() {
  const [tgId, setTgId] = useState(7);
  const [submitted, setSubmitted] = useState(7);

  const onSubmit = (e) => {
    e.preventDefault();
    if (!tgId) return;
    setSubmitted(tgId);
  };

  return (
    <div className='main_app'>
      <h2>Дерево пользователей</h2>
      <form onSubmit={onSubmit} style={{ marginBottom: 12 }}>
        <input
          placeholder="Введите tg_id (число)"
          value={tgId}
          onChange={(e) => setTgId(e.target.value)}
          style={{ padding: 8, width: 240 }}
        />
        <button style={{ marginLeft: 8, padding: '8px 12px' }}>Показать</button>
      </form>

      {submitted && <UserTree tgId={submitted} apiBase="http://localhost:8000" />}
      {!submitted && <div>Введите tg_id и нажмите "Показать".</div>}
    </div>
  );
}

export default App;
