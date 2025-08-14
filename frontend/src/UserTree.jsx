import React, { useEffect, useRef, useState } from "react";
import Tree from "react-d3-tree";

// Трансформируем ответ бэка -> формат react-d3-tree.
// name оставляем пустым, чтобы не рисовался дефолтный текст под нодой.
function transformNode(node) {
  return {
    name: node.username || `tg_${node.tg_id}`,                           // скрываем дефолтный label
    children: (node.children || []).map(transformNode),
  };
}

// Кастомный HTML-лейбл с белым фоном.
// pointerEvents: 'none' — чтобы клики шли по ноде (сворачивание/разворачивание).
const CustomLabel = ({ nodeData }) => {
  console.log(nodeData);
  return (
    <svg
      style={{
        background: "#fff",
        padding: "2px 6px",
        borderRadius: 4,
        boxShadow: "0 0 0 1px rgba(0,0,0,0.25)",
        fontSize: 12,
        fontWeight: 600,
        whiteSpace: "nowrap",
        pointerEvents: "none",
        transform: "translateY(-10px)", // поднять текст на 10px
      }}
    >
      {nodeData.__label}
    </svg>
  )


};

export default function UserTree({ tgId, apiBase }) {
  const [treeData, setTreeData] = useState(null);
  const treeRef = useRef(null);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const el = treeRef.current;
    if (el) setTranslate({ x: el.offsetWidth / 2, y: 80 });
  }, [treeRef.current]);

  useEffect(() => {
    (async () => {
      const res = await fetch(`${apiBase}/users/${tgId}/structure`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setTreeData(transformNode(data));
    })().catch((e) => {
      console.error(e);
      setTreeData(null);
    });
  }, [tgId, apiBase]);

  if (!treeData) return <div>Загрузка дерева…</div>;

  // Размер и позиция foreignObject для лейбла (ширину можно увеличить при длинных именах)
  const LABEL_W = 140;
  const LABEL_H = 28;

  return (
    <div
      ref={treeRef}
      style={{ width: "100%", height: 700, border: "1px solid #eee", overflow: "hidden" }}
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
        nodeLabelComponent={{
          render: <CustomLabel />,
          foreignObjectWrapper: {
            x: -LABEL_W / 2, // центрируем над нодой
            y: -LABEL_H - 14, // базовое поднятие над кружком (чтобы не налезало)
            width: LABEL_W,
            height: LABEL_H,
          },
        }}
      />
    </div>
  );
}
