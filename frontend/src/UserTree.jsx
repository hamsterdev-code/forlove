import React, { useEffect, useRef, useState } from "react";
import Tree from "react-d3-tree";
import axios from "axios"
import Modal from "./Modal";
import { BASE_URL } from "./constants";
// Конвертация данных в формат дерева
function transformNode(node) {
  return {
    name: node.username || `tg_${node.tg_id}`,
    children: (node.children || []).map(transformNode),
  };
}


export default function UserTree({ tgId }) {
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
          setSelectedUsername(element.textContent)
        }
      }
    }, 1000);
  }, [treeRef.current]);


  useEffect(() => {
    (async () => {
      const res = await fetch(`${BASE_URL}/users/${tgId}/structure`);
      if (!res.ok) alert("Пользователь не найден. Вернитесь в бота")
      const data = await res.json();
      setTreeData(transformNode(data));
    })();
  }, [tgId, BASE_URL]);

  if (!treeData) return <div>Загрузка дерева…</div>;

  return (
    <>
      <div
        ref={treeRef}
        style={{ width: "99%", height: "99%" }}
      >
        <Tree
          data={treeData}
          translate={translate}
          orientation="vertical"
          pathFunc="elbow"
          collapsible
          initialDepth={3}
          nodeSize={{ x: 100, y: 120 }}
          separation={{ siblings: 1.5, nonSiblings: 2 }}
          zoomable
          scaleExtent={{ min: 0.1, max: 2 }}
          renderCustomNodeElement={({ nodeDatum, toggleNode }) => {
            const paddingX = 8; // горизонтальный паддинг
            const paddingY = 6; // вертикальный паддинг
            const textWidth = nodeDatum.name.length * 7; // ширина текста
            const rectWidth = textWidth + paddingX * 2;
            const rectHeight = 16 + paddingY * 2;

            return (
              <g>
                {/* Круг */}
                <circle
                  r={15}
                  fill={nodeDatum.children && nodeDatum.children.length > 0 ? "#555" : "#fff"}
                  stroke="black"
                  strokeWidth={1.5}
                  onClick={toggleNode}
                  style={{ cursor: "pointer" }}
                />

                {/* Текст с белым фоном */}
                <g transform="translate(0, -35)">
                  <rect
                    x={-(rectWidth / 2)}
                    y={-(rectHeight / 2)}
                    width={rectWidth}
                    height={rectHeight}
                    fill="white"
                    rx={6}
                    ry={6}
                    stroke="none"        // отключаем рамку
                    strokeWidth={0}      // гарантированно убираем толщину
                  />
                  <text
                    textAnchor="middle"
                    alignmentBaseline="middle"
                    className="rd3t-label__title"

                  >
                    {nodeDatum.name}
                  </text>
                </g>
              </g>
            );
          }}
        />

      </div>

      {/* Модалка */}
      <Modal username={selectedUsername} onClose={() => setSelectedUsername(null)} />
    </>
  );
}
