import React, { useState } from "react";

export default function GraphWithModal({ nodes }) {
  const [selectedUser, setSelectedUser] = useState(null);

  const handleNodeClick = (user) => {
    setSelectedUser(user);
  };

  const closeModal = () => {
    setSelectedUser(null);
  };

  return (
    <div>
      {/* Здесь твой рендер графа */}
      <div className="graph">
        {nodes.map((node) => (
          <div
            key={node.id}
            className="node"
            onClick={() => handleNodeClick(node)}
            style={{
              display: "inline-block",
              padding: "10px",
              border: "1px solid black",
              margin: "5px",
              cursor: "pointer",
            }}
          >
            {node.label}
          </div>
        ))}
      </div>

      {/* Модалка */}
      {selectedUser && (
        <div
          className="modal-overlay"
          onClick={closeModal}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 999,
          }}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()} // чтобы клик внутри модалки её не закрывал
            style={{
              backgroundColor: "#fff",
              padding: "20px 30px",
              borderRadius: "8px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.3)",
              minWidth: "300px",
              textAlign: "center",
            }}
          >
            <h2>username: {selectedUser.username}</h2>
            <button
              onClick={closeModal}
              style={{
                marginTop: "15px",
                padding: "8px 15px",
                background: "#007bff",
                color: "#fff",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
              }}
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
