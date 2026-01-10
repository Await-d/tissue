import{ar as e,a2 as l,ab as i,r as c,F as a,as as o,ak as d,at as p,O as b}from"./index-CPAKaPzh.js";import{L as u}from"./logo-D6Xba1mH.js";import{R as x}from"./LockOutlined-Bop63oxz.js";function y(){const[n]=e.useForm(),{logging:t}=l(r=>r.auth),{login:s}=i().auth;return c.useEffect(()=>{document.body.style.backgroundColor="#0d0d0f"},[]),a.jsxs("div",{className:"h-dvh flex flex-col justify-center items-center relative overflow-hidden",style:{background:"linear-gradient(135deg, #0d0d0f 0%, #141416 50%, #0d0d0f 100%)"},children:[a.jsx("div",{className:"absolute top-1/4 -left-32 w-96 h-96 rounded-full opacity-5 blur-3xl",style:{background:"radial-gradient(circle, #d4a852 0%, transparent 70%)",animation:"pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite"}}),a.jsx("div",{className:"absolute bottom-1/4 -right-32 w-96 h-96 rounded-full opacity-5 blur-3xl",style:{background:"radial-gradient(circle, #e8c780 0%, transparent 70%)",animation:"pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite 2s"}}),a.jsxs("div",{className:"flex mb-10 relative",style:{animation:"tissueLogoEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards",opacity:0},children:[a.jsx("div",{className:"absolute inset-0 blur-2xl opacity-40",style:{background:"radial-gradient(circle, #d4a852 0%, transparent 70%)"}}),a.jsx("img",{className:"h-20 relative z-10",src:u,alt:"TISSUE+",style:{filter:"drop-shadow(0 0 20px rgba(212, 168, 82, 0.3))"}})]}),a.jsxs("div",{className:"w-[380px] relative",style:{animation:"tissueCardEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards",opacity:0},children:[a.jsxs("div",{className:"p-8 rounded-2xl relative overflow-hidden",style:{background:"rgba(26, 26, 29, 0.6)",backdropFilter:"blur(40px) saturate(180%)",WebkitBackdropFilter:"blur(40px) saturate(180%)",border:"1px solid rgba(255, 255, 255, 0.08)",boxShadow:"0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)"},children:[a.jsx("div",{className:"absolute top-0 left-0 right-0 h-px",style:{background:"linear-gradient(90deg, transparent 0%, rgba(212, 168, 82, 0.3) 50%, transparent 100%)"}}),a.jsxs(e,{size:"large",form:n,onFinish:r=>s(r),style:{"--ant-color-bg-container":"#1a1a1d","--ant-color-border":"rgba(255, 255, 255, 0.08)","--ant-color-primary":"#d4a852","--ant-color-text":"#f0f0f2","--ant-color-text-placeholder":"#6a6a72"},children:[a.jsx(e.Item,{name:"username",children:a.jsx(o,{prefix:a.jsx(d,{style:{color:"#6a6a72",fontSize:"16px"}}),placeholder:"用户名",style:{height:"48px",backgroundColor:"#141416",border:"1px solid rgba(255, 255, 255, 0.08)",borderRadius:"10px",color:"#f0f0f2",fontSize:"15px",transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)"},onFocus:r=>{r.target.style.backgroundColor="#1a1a1d",r.target.style.borderColor="#d4a852",r.target.style.boxShadow="0 0 0 2px rgba(212, 168, 82, 0.1)"},onBlur:r=>{r.target.style.backgroundColor="#141416",r.target.style.borderColor="rgba(255, 255, 255, 0.08)",r.target.style.boxShadow="none"}})}),a.jsx(e.Item,{name:"password",children:a.jsx(o.Password,{prefix:a.jsx(x,{style:{color:"#6a6a72",fontSize:"16px"}}),placeholder:"密码",style:{height:"48px",backgroundColor:"#141416",border:"1px solid rgba(255, 255, 255, 0.08)",borderRadius:"10px",color:"#f0f0f2",fontSize:"15px",transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)"},onFocus:r=>{r.target.parentElement.style.backgroundColor="#1a1a1d",r.target.parentElement.style.borderColor="#d4a852",r.target.parentElement.style.boxShadow="0 0 0 2px rgba(212, 168, 82, 0.1)"},onBlur:r=>{r.target.parentElement.style.backgroundColor="#141416",r.target.parentElement.style.borderColor="rgba(255, 255, 255, 0.08)",r.target.parentElement.style.boxShadow="none"}})}),a.jsx(e.Item,{noStyle:!0,name:"remember",valuePropName:"checked",children:a.jsx(p,{style:{marginBottom:24,color:"#a0a0a8",fontSize:"14px"},children:"保持登录"})}),a.jsx(b,{type:"primary",htmlType:"submit",loading:t,style:{width:"100%",height:"48px",background:"linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)",border:"none",borderRadius:"10px",fontSize:"16px",fontWeight:600,color:"#0d0d0f",boxShadow:"0 4px 16px rgba(212, 168, 82, 0.25)",transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",cursor:t?"not-allowed":"pointer"},onMouseEnter:r=>{t||(r.currentTarget.style.background="linear-gradient(135deg, #e8c780 0%, #d4a852 100%)",r.currentTarget.style.boxShadow="0 0 24px rgba(212, 168, 82, 0.4), 0 8px 24px rgba(0, 0, 0, 0.3)",r.currentTarget.style.transform="translateY(-2px)")},onMouseLeave:r=>{t||(r.currentTarget.style.background="linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)",r.currentTarget.style.boxShadow="0 4px 16px rgba(212, 168, 82, 0.25)",r.currentTarget.style.transform="translateY(0)")},onMouseDown:r=>{t||(r.currentTarget.style.transform="translateY(0) scale(0.98)")},onMouseUp:r=>{t||(r.currentTarget.style.transform="translateY(-2px) scale(1)")},children:t?"登录中...":"登录"})]})]}),a.jsx("div",{className:"absolute -bottom-10 left-1/2 -translate-x-1/2 w-3/4 h-20 blur-3xl opacity-20 pointer-events-none",style:{background:"radial-gradient(ellipse, #d4a852 0%, transparent 70%)"}})]}),a.jsx("div",{className:"absolute bottom-8 text-center",style:{color:"#6a6a72",fontSize:"13px",animation:"tissueFadeIn 1s ease-out 0.4s forwards",opacity:0},children:a.jsx("div",{children:"TISSUE+ · 暗黑电影美学"})}),a.jsx("style",{children:`
                @keyframes tissueLogoEnter {
                    0% {
                        opacity: 0;
                        transform: translateY(-20px) scale(0.9);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }

                @keyframes tissueCardEnter {
                    0% {
                        opacity: 0;
                        transform: translateY(30px) scale(0.95);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }

                @keyframes tissueFadeIn {
                    0% {
                        opacity: 0;
                    }
                    100% {
                        opacity: 1;
                    }
                }

                @keyframes pulse {
                    0%, 100% {
                        transform: scale(1);
                        opacity: 0.05;
                    }
                    50% {
                        transform: scale(1.1);
                        opacity: 0.08;
                    }
                }

                /* Ant Design 输入框样式覆盖 */
                .ant-input,
                .ant-input-password {
                    background-color: #141416 !important;
                    border: 1px solid rgba(255, 255, 255, 0.08) !important;
                    color: #f0f0f2 !important;
                }

                .ant-input::placeholder,
                .ant-input-password input::placeholder {
                    color: #6a6a72 !important;
                }

                .ant-input:focus,
                .ant-input-password:focus,
                .ant-input-password-focused,
                .ant-input:hover,
                .ant-input-password:hover {
                    background-color: #1a1a1d !important;
                    border-color: #d4a852 !important;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.1) !important;
                }

                .ant-input-password .ant-input {
                    background-color: transparent !important;
                    border: none !important;
                }

                .ant-input-suffix {
                    color: #6a6a72 !important;
                }

                .ant-checkbox-wrapper {
                    color: #a0a0a8 !important;
                }

                .ant-checkbox-inner {
                    background-color: #141416 !important;
                    border-color: rgba(255, 255, 255, 0.08) !important;
                }

                .ant-checkbox-checked .ant-checkbox-inner {
                    background-color: #d4a852 !important;
                    border-color: #d4a852 !important;
                }

                .ant-checkbox:hover .ant-checkbox-inner {
                    border-color: #d4a852 !important;
                }

                .ant-form-item {
                    margin-bottom: 20px;
                }

                .ant-form-item-explain-error {
                    color: #ff4d4f !important;
                    font-size: 13px;
                    margin-top: 4px;
                }
            `})]})}export{y as component};
