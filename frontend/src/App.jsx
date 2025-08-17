import React, { useEffect, useState } from 'react';
import UserTree from './UserTree';

function App() {
  const [tgId, setTgId] = useState(null);
  const [submitted, setSubmitted] = useState(null);

  useEffect(()=>{
    setTgId(parseInt(window.location.href.split("?")[1]))
    setSubmitted(true)
  }, [])

  return (
    <div className='main_app'>
      <div className="main_text">
        <p>Для открытия стркуктуры пользователя нажмите на полный круг около ника</p>
        <p>Для просмотра подробной информации пользователя нажмите на его никнейм</p>
      </div>
      {submitted && <UserTree tgId={tgId} />}
      {!submitted && <div>Загрузка...</div>}
    </div>
  );
}

export default App;
