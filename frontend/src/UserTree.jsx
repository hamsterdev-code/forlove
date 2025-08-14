import React, { useEffect, useRef, useState } from "react";
import Tree from "react-d3-tree";

// Конвертация данных в формат дерева
function transformNode(node) {
  return {
    name: node.username || `tg_${node.tg_id}`,
    children: (node.children || []).map(transformNode),
  };
}

// HTML-лейбл
const CustomLabel = ({ nodeData }) => {
  return (
    <div
      style={{
        background: "#fff",
        padding: "4px 8px",
        borderRadius: 6,
        boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
        fontSize: 12,
        fontWeight: 600,
        whiteSpace: "nowrap",
        transform: "translateY(-10px)",
      }}
    >
      {nodeData.name}
    </div>
  );
};

// Модалка
const Modal = ({ username, onClose }) => {
  if (!username) return null;
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
        <p style={{ margin: 0, fontSize: 16 }}>
          <strong>username:</strong> {username}
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

export default function UserTree({ tgId, apiBase }) {
  const [treeData, setTreeData] = useState(null);
  const [selectedUsername, setSelectedUsername] = useState(null);
  const treeRef = useRef(null);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const el = treeRef.current;
    if (el) setTranslate({ x: el.offsetWidth / 2, y: 80 });
    setInterval(() => {
      const labels = document.querySelectorAll(".rd3t-label__title")
      for (let i = 0; i < labels.length; i++) {
        const element = labels[i];
        element.onclick = function () {
          console.log(element.textContent);
          alert("alert");
        }
      }
    }, 1000);
  }, [treeRef.current]);


  useEffect(() => {
    (async () => {
      const res = await fetch(`${apiBase}/users/${tgId}/structure`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setTreeData(transformNode(data));
    })();
  }, [tgId, apiBase]);

  if (!treeData) return <div>Загрузка дерева…</div>;

  const LABEL_W = 160;
  const LABEL_H = 30;

  return (
    <>
      <div
        ref={treeRef}
        style={{ width: "100%", height: 700, border: "1px solid #eee" }}
      >
        <Tree
          data={treeData}
          translate={translate}
          orientation="vertical"
          pathFunc="elbow"
          collapsible={true}          // сворачивание/разворачивание
          initialDepth={3}            // раскрыты только первые уровни
          nodeSize={{ x: 160, y: 120 }}
          separation={{ siblings: 1.5, nonSiblings: 2 }}
          zoomable={true}
          scaleExtent={{ min: 0.1, max: 2 }}
          allowForeignObjects={true}  // ВАЖНО: разрешаем HTML внутри SVG
        />
      </div>

      {/* Модалка */}
      <Modal username={selectedUsername} onClose={() => setSelectedUsername(null)} />
    </>
  );
}
