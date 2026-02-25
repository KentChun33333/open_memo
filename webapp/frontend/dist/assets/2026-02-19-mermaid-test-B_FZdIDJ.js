import{j as e}from"./index-B2GV5NfK.js";const r={title:"Mermaid and Table Test",date:"2026-02-19",tags:["test","utility"]};function s(n){const t={code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",...n.components};return e.jsxs(e.Fragment,{children:[e.jsx(t.h1,{children:"Testing Markdown Enhancements"}),`
`,e.jsx(t.p,{children:"This post verifies that GFM tables and Mermaid diagrams are rendering correctly."}),`
`,e.jsx(t.h2,{children:"GFM Table"}),`
`,e.jsxs(t.table,{children:[e.jsx(t.thead,{children:e.jsxs(t.tr,{children:[e.jsx(t.th,{style:{textAlign:"left"},children:"Feature"}),e.jsx(t.th,{style:{textAlign:"left"},children:"Support"}),e.jsx(t.th,{style:{textAlign:"left"},children:"Status"})]})}),e.jsxs(t.tbody,{children:[e.jsxs(t.tr,{children:[e.jsx(t.td,{style:{textAlign:"left"},children:"Tables"}),e.jsx(t.td,{style:{textAlign:"left"},children:"Yes"}),e.jsx(t.td,{style:{textAlign:"left"},children:"✅ Working"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{style:{textAlign:"left"},children:"Mermaid Diagrams"}),e.jsx(t.td,{style:{textAlign:"left"},children:"Yes"}),e.jsx(t.td,{style:{textAlign:"left"},children:"✅ Working"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{style:{textAlign:"left"},children:"Code Syntax"}),e.jsx(t.td,{style:{textAlign:"left"},children:"Yes"}),e.jsx(t.td,{style:{textAlign:"left"},children:"✅ Existing"})]})]})]}),`
`,e.jsx(t.h2,{children:"Mermaid Diagram"}),`
`,e.jsx(t.pre,{children:e.jsx(t.code,{className:"language-mermaid",children:`graph TD;
    A[Start] --> B{Is it working?};
    B -- Yes --> C[Great!];
    B -- No --> D[Debug time...];
    C --> E[Done];
    D --> B;
`})}),`
`,e.jsx(t.p,{children:"Another one:"}),`
`,e.jsx(t.pre,{children:e.jsx(t.code,{className:"language-mermaid",children:`pie title Pets adoption number
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
`})})]})}function i(n={}){const{wrapper:t}=n.components||{};return t?e.jsx(t,{...n,children:e.jsx(s,{...n})}):s(n)}export{i as default,r as frontmatter};
