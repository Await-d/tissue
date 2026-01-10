import{F as o,al as u,ar as t,as as m,aZ as x,at as h,aL as b,a7 as y,aA as p,aN as j,au as l,S as k,ac as v,J as f,aC as w,X as S,aD as z,V as I,U as N,N as c,af as C}from"./index-CPAKaPzh.js";function F(a){const{form:s,initValues:d,...i}=a;return o.jsxs(o.Fragment,{children:[o.jsx("style",{children:`
                .site-modify-modal .ant-modal-content {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(20px);
                }

                .site-modify-modal .ant-modal-header {
                    background: transparent;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .site-modify-modal .ant-modal-title {
                    color: #f0f0f2;
                    font-weight: 600;
                    font-size: 16px;
                }

                .site-modify-modal .ant-modal-close {
                    color: #a0a0a8;
                }

                .site-modify-modal .ant-modal-close:hover {
                    color: #f0f0f2;
                    background: rgba(255, 255, 255, 0.08);
                }

                .site-modify-modal .ant-form-item-label > label {
                    color: #f0f0f2;
                    font-weight: 500;
                }

                .site-modify-modal .ant-input,
                .site-modify-modal .ant-select-selector {
                    background: #141416 !important;
                    border: 1px solid rgba(255, 255, 255, 0.12) !important;
                    color: #f0f0f2 !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-input:hover,
                .site-modify-modal .ant-select-selector:hover {
                    border-color: rgba(212, 168, 82, 0.4) !important;
                }

                .site-modify-modal .ant-input:focus,
                .site-modify-modal .ant-select-focused .ant-select-selector {
                    border-color: #d4a852 !important;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.15) !important;
                }

                .site-modify-modal .ant-input::placeholder {
                    color: #6a6a72;
                }

                .site-modify-modal .ant-select-arrow {
                    color: #a0a0a8;
                }

                .site-modify-modal .ant-checkbox-wrapper {
                    color: #f0f0f2;
                }

                .site-modify-modal .ant-checkbox-inner {
                    background: #141416;
                    border-color: rgba(255, 255, 255, 0.12);
                }

                .site-modify-modal .ant-checkbox-checked .ant-checkbox-inner {
                    background: #d4a852;
                    border-color: #d4a852;
                }

                .site-modify-modal .ant-checkbox-wrapper:hover .ant-checkbox-inner {
                    border-color: rgba(212, 168, 82, 0.4);
                }

                .site-modify-modal .ant-modal-footer {
                    border-top: 1px solid rgba(255, 255, 255, 0.08);
                }

                .site-modify-modal .ant-btn-primary {
                    background: #d4a852;
                    border-color: #d4a852;
                    color: #0d0d0f;
                    font-weight: 600;
                    box-shadow: 0 2px 8px rgba(212, 168, 82, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-primary:hover {
                    background: #e8c780 !important;
                    border-color: #e8c780 !important;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4) !important;
                    transform: translateY(-1px);
                }

                .site-modify-modal .ant-btn-default {
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #a0a0a8;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-default:hover {
                    border-color: rgba(255, 255, 255, 0.2) !important;
                    color: #f0f0f2 !important;
                    background: rgba(255, 255, 255, 0.05) !important;
                }

                .site-modify-modal .ant-select-dropdown {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                }

                .site-modify-modal .ant-select-item {
                    color: #a0a0a8;
                }

                .site-modify-modal .ant-select-item-option-selected {
                    background: rgba(212, 168, 82, 0.15);
                    color: #d4a852;
                    font-weight: 500;
                }

                .site-modify-modal .ant-select-item-option-active {
                    background: rgba(255, 255, 255, 0.05);
                }
            `}),o.jsx(u,{...i,title:d.name,className:"site-modify-modal",children:o.jsxs(t,{form:s,layout:"vertical",children:[o.jsx(t.Item,{noStyle:!0,name:"id",children:o.jsx(m,{style:{display:"none"}})}),o.jsx(t.Item,{name:"alternate_host",label:"替代域名",children:o.jsx(m,{placeholder:"当域名失效或替代域名时填写"})}),o.jsx(t.Item,{name:"priority",label:"优先级",initialValue:0,children:o.jsx(x,{children:Array(101).fill(0).map((n,r)=>o.jsx(x.Option,{value:r,children:r},r))})}),o.jsx(t.Item,{name:"status",label:"状态",valuePropName:"checked",children:o.jsx(h,{children:"启用"})})]})})]})}async function B(){return(await b.get("/site/")).data.data}function M(a){return b.put("/site/",a)}function E(){return b.post("/site/testing")}function R(){y.useToken();const{data:a,refresh:s,loading:d}=p(B,{}),{modalProps:i,setOpen:n}=j({service:M,onOk:()=>{n(!1),s()}}),{run:r}=p(E,{manual:!0,onSuccess:()=>{C.success("站点刷新提交成功")}});function g(e){return o.jsx(f.Item,{children:o.jsx(I.Ribbon,{text:e.status?"启用":"停用",color:e.status?"#d4a852":"#6a6a72",style:{fontSize:"12px",fontWeight:500},children:o.jsx(l,{size:"default",title:o.jsxs("div",{className:"flex items-center gap-2",children:[o.jsx(c,{variant:"borderless",style:{background:"rgba(212, 168, 82, 0.15)",color:"#d4a852",border:"1px solid rgba(212, 168, 82, 0.3)",fontWeight:600,minWidth:"32px",textAlign:"center"},children:e.priority}),o.jsx("div",{style:{color:"#f0f0f2",fontWeight:500},children:e.name})]}),className:"cursor-pointer site-card",onClick:()=>n(!0,e),style:{background:"#1a1a1d",border:"1px solid rgba(255, 255, 255, 0.08)",boxShadow:"0 2px 8px rgba(0, 0, 0, 0.3)",transition:"all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",overflow:"hidden"},styles:{header:{background:"#222226",borderBottom:"1px solid rgba(255, 255, 255, 0.08)",padding:"12px 16px"},body:{padding:"16px"}},children:o.jsxs(N,{direction:"vertical",size:"large",style:{width:"100%"},children:[o.jsx("div",{style:{color:"#a0a0a8",fontSize:"13px",lineHeight:"1.5"},children:o.jsx("span",{children:e.alternate_host||"未设置替代域名"})}),o.jsxs("div",{className:"flex gap-2",children:[o.jsx(c,{color:"blue",variant:"borderless",style:{background:"rgba(24, 144, 255, 0.15)",border:"1px solid rgba(24, 144, 255, 0.3)",color:"#69b1ff"},children:"元数据"}),e.downloadable&&o.jsx(c,{color:"green",variant:"borderless",style:{background:"rgba(82, 196, 26, 0.15)",border:"1px solid rgba(82, 196, 26, 0.3)",color:"#95de64"},children:"下载"})]})]})})})})}return d?o.jsx(l,{style:{background:"#1a1a1d",border:"1px solid rgba(255, 255, 255, 0.08)"},children:o.jsx(k,{active:!0})}):o.jsxs(o.Fragment,{children:[o.jsx("style",{children:`
                .site-card:hover {
                    transform: translateY(-4px);
                    border-color: rgba(212, 168, 82, 0.4) !important;
                    box-shadow: 0 8px 24px rgba(212, 168, 82, 0.15), 0 0 0 1px rgba(212, 168, 82, 0.2) !important;
                }

                .site-card .ant-card-head-title {
                    padding: 0;
                }
            `}),a&&a.length>0?o.jsx(f,{grid:{gutter:16,xxl:4,xl:4,lg:4,md:2,xs:1},dataSource:a,renderItem:g}):o.jsx(l,{title:"站点",style:{background:"#1a1a1d",border:"1px solid rgba(255, 255, 255, 0.08)"},styles:{header:{background:"#222226",borderBottom:"1px solid rgba(255, 255, 255, 0.08)",color:"#f0f0f2"}},children:o.jsx(w,{description:o.jsxs("div",{style:{color:"#a0a0a8"},children:[o.jsx("div",{children:"无可用站点"}),o.jsxs("div",{children:["请检查网络连接后"," ",o.jsx("a",{onClick:()=>r(),style:{color:"#d4a852",textDecoration:"underline",cursor:"pointer"},children:"刷新站点"})]})]})})}),o.jsx(F,{...i}),v.createPortal(o.jsx(o.Fragment,{children:o.jsx(S,{icon:o.jsx(z,{}),onClick:()=>r(),style:{background:"#d4a852",boxShadow:"0 4px 12px rgba(212, 168, 82, 0.3)"}})}),document.getElementsByClassName("index-float-button-group")[0])]})}export{R as component};
