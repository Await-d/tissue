import{W as h,F as r,am as f,as as d,at as x,a$ as g,au as $,aM as b,a8 as k,aB as p,aO as j,av as c,S as P,ad as v,J as y,aD as w,Y as S,aE as C,V as z,U as B,N as m,ag as I}from"./index-mgZE0TJV.js";function E(e){const{form:i,initValues:l,...s}=e,o=h();return r.jsxs(r.Fragment,{children:[r.jsx("style",{children:`
                .site-modify-modal .ant-modal-content {
                    background: ${o.modalBg};
                    border: 1px solid ${o.borderPrimary};
                    box-shadow: 0 12px 48px ${o.rgba("black",.6)};
                    backdrop-filter: blur(20px);
                }

                .site-modify-modal .ant-modal-mask {
                    background: ${o.modalOverlay};
                }

                .site-modify-modal .ant-modal-header {
                    background: transparent;
                    border-bottom: 1px solid ${o.borderPrimary};
                }

                .site-modify-modal .ant-modal-title {
                    color: ${o.textPrimary};
                    font-weight: 600;
                    font-size: 16px;
                }

                .site-modify-modal .ant-modal-close {
                    color: ${o.textSecondary};
                }

                .site-modify-modal .ant-modal-close:hover {
                    color: ${o.textPrimary};
                    background: ${o.borderPrimary};
                }

                .site-modify-modal .ant-form-item-label > label {
                    color: ${o.textPrimary};
                    font-weight: 500;
                }

                .site-modify-modal .ant-input,
                .site-modify-modal .ant-select-selector {
                    background: ${o.bgElevated} !important;
                    border: 1px solid ${o.borderPrimary} !important;
                    color: ${o.textPrimary} !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-input:hover,
                .site-modify-modal .ant-select-selector:hover {
                    border-color: ${o.rgba("gold",.4)} !important;
                }

                .site-modify-modal .ant-input:focus,
                .site-modify-modal .ant-select-focused .ant-select-selector {
                    border-color: ${o.goldPrimary} !important;
                    box-shadow: 0 0 0 2px ${o.goldGlow} !important;
                }

                .site-modify-modal .ant-input::placeholder {
                    color: ${o.textTertiary};
                }

                .site-modify-modal .ant-select-arrow {
                    color: ${o.textSecondary};
                }

                .site-modify-modal .ant-checkbox-wrapper {
                    color: ${o.textPrimary};
                }

                .site-modify-modal .ant-checkbox-inner {
                    background: ${o.bgElevated};
                    border-color: ${o.borderPrimary};
                }

                .site-modify-modal .ant-checkbox-checked .ant-checkbox-inner {
                    background: ${o.goldPrimary};
                    border-color: ${o.goldPrimary};
                }

                .site-modify-modal .ant-checkbox-wrapper:hover .ant-checkbox-inner {
                    border-color: ${o.rgba("gold",.4)};
                }

                .site-modify-modal .ant-modal-footer {
                    border-top: 1px solid ${o.borderPrimary};
                }

                .site-modify-modal .ant-btn-primary {
                    background: ${o.goldPrimary};
                    border-color: ${o.goldPrimary};
                    color: ${o.bgBase};
                    font-weight: 600;
                    box-shadow: 0 2px 8px ${o.rgba("gold",.3)};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-primary:hover {
                    background: ${o.goldLight} !important;
                    border-color: ${o.goldLight} !important;
                    box-shadow: 0 4px 12px ${o.rgba("gold",.4)} !important;
                    transform: translateY(-1px);
                }

                .site-modify-modal .ant-btn-default {
                    background: transparent;
                    border: 1px solid ${o.borderPrimary};
                    color: ${o.textSecondary};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-default:hover {
                    border-color: ${o.rgba("white",.2)} !important;
                    color: ${o.textPrimary} !important;
                    background: ${o.rgba("white",.05)} !important;
                }

                .site-modify-modal .ant-select-dropdown {
                    background: ${o.bgContainer};
                    border: 1px solid ${o.borderPrimary};
                    box-shadow: 0 8px 24px ${o.rgba("black",.5)};
                }

                .site-modify-modal .ant-select-item {
                    color: ${o.textSecondary};
                }

                .site-modify-modal .ant-select-item-option-selected {
                    background: ${o.goldGlow};
                    color: ${o.goldPrimary};
                    font-weight: 500;
                }

                .site-modify-modal .ant-select-item-option-active {
                    background: ${o.rgba("white",.05)};
                }
            `}),r.jsx(f,{...s,title:l.name,className:"site-modify-modal",children:r.jsxs(d,{form:i,layout:"vertical",children:[r.jsx(d.Item,{noStyle:!0,name:"id",children:r.jsx(x,{style:{display:"none"}})}),r.jsx(d.Item,{name:"alternate_host",label:"替代域名",children:r.jsx(x,{placeholder:"当域名失效或替代域名时填写"})}),r.jsx(d.Item,{name:"priority",label:"优先级",initialValue:0,children:r.jsx(g,{children:Array(101).fill(0).map((n,a)=>r.jsx(g.Option,{value:a,children:a},a))})}),r.jsx(d.Item,{name:"status",label:"状态",valuePropName:"checked",children:r.jsx($,{children:"启用"})})]})})]})}async function F(){return(await b.get("/site/")).data.data}function N(e){return b.put("/site/",e)}function M(){return b.post("/site/testing")}function O(){const e=h();k.useToken();const{data:i,refresh:l,loading:s}=p(F,{}),{modalProps:o,setOpen:n}=j({service:N,onOk:()=>{n(!1),l()}}),{run:a}=p(M,{manual:!0,onSuccess:()=>{I.success("站点刷新提交成功")}});function u(t){return r.jsx(y.Item,{children:r.jsx(z.Ribbon,{text:t.status?"启用":"停用",color:t.status?e.goldPrimary:e.textTertiary,style:{fontSize:"12px",fontWeight:500},children:r.jsx(c,{size:"default",title:r.jsxs("div",{className:"flex items-center gap-2",children:[r.jsx(m,{style:{background:e.rgba("gold",.15),color:e.goldPrimary,border:`1px solid ${e.borderGold}`,fontWeight:600,minWidth:"32px",textAlign:"center"},children:t.priority}),r.jsx("div",{style:{color:e.textPrimary,fontWeight:500},children:t.name})]}),className:"cursor-pointer site-card",onClick:()=>n(!0,t),style:{background:e.bgContainer,border:`1px solid ${e.borderPrimary}`,boxShadow:`0 2px 8px ${e.rgba("black",.3)}`,transition:"all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",overflow:"hidden"},styles:{header:{background:e.bgSpotlight,borderBottom:`1px solid ${e.borderPrimary}`,padding:"12px 16px"},body:{padding:"16px"}},children:r.jsxs(B,{direction:"vertical",size:"large",style:{width:"100%"},children:[r.jsx("div",{style:{color:e.textSecondary,fontSize:"13px",lineHeight:"1.5"},children:r.jsx("span",{children:t.alternate_host||"未设置替代域名"})}),r.jsxs("div",{className:"flex gap-2",children:[r.jsx(m,{color:"blue",style:{background:"rgba(24, 144, 255, 0.15)",border:"1px solid rgba(24, 144, 255, 0.3)",color:"#69b1ff"},children:"元数据"}),t.downloadable&&r.jsx(m,{color:"green",style:{background:"rgba(82, 196, 26, 0.15)",border:"1px solid rgba(82, 196, 26, 0.3)",color:"#95de64"},children:"下载"})]})]})})})})}return s?r.jsx(c,{style:{background:e.bgContainer,border:`1px solid ${e.borderPrimary}`},children:r.jsx(P,{active:!0})}):r.jsxs(r.Fragment,{children:[r.jsx("style",{children:`
                .site-card:hover {
                    transform: translateY(-4px);
                    border-color: ${e.rgba("gold",.4)} !important;
                    box-shadow: 0 8px 24px ${e.rgba("gold",.15)}, 0 0 0 1px ${e.rgba("gold",.2)} !important;
                }

                .site-card .ant-card-head-title {
                    padding: 0;
                }
            `}),i&&i.length>0?r.jsx(y,{grid:{gutter:16,xxl:4,xl:4,lg:4,md:2,xs:1},dataSource:i,renderItem:u}):r.jsx(c,{title:"站点",style:{background:e.bgContainer,border:`1px solid ${e.borderPrimary}`},styles:{header:{background:e.bgSpotlight,borderBottom:`1px solid ${e.borderPrimary}`,color:e.textPrimary}},children:r.jsx(w,{description:r.jsxs("div",{style:{color:e.textSecondary},children:[r.jsx("div",{children:"无可用站点"}),r.jsxs("div",{children:["请检查网络连接后"," ",r.jsx("a",{onClick:()=>a(),style:{color:e.goldPrimary,textDecoration:"underline",cursor:"pointer"},children:"刷新站点"})]})]})})}),r.jsx(E,{...o}),v.createPortal(r.jsx(r.Fragment,{children:r.jsx(S,{icon:r.jsx(C,{}),onClick:()=>a(),style:{background:e.goldPrimary,boxShadow:`0 4px 12px ${e.rgba("gold",.3)}`}})}),document.getElementsByClassName("index-float-button-group")[0])]})}export{O as component};
