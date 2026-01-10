import{as as o,a3 as i,ac as c,W as d,r as p,F as e,at as n,al as b,au as g,O as m}from"./index-g83hHc8K.js";import{L as u}from"./logo-D6Xba1mH.js";import{R as x}from"./LockOutlined-D90Ee_Jv.js";function k(){const[s]=o.useForm(),{logging:a}=i(t=>t.auth),{login:l}=c().auth,r=d();return p.useEffect(()=>{document.body.style.backgroundColor=r.bgBase},[r]),e.jsxs("div",{className:"h-dvh flex flex-col justify-center items-center relative overflow-hidden",style:{background:`linear-gradient(135deg, ${r.bgBase} 0%, ${r.bgElevated} 50%, ${r.bgBase} 100%)`},children:[e.jsx("div",{className:"absolute top-1/4 -left-32 w-96 h-96 rounded-full opacity-5 blur-3xl",style:{background:`radial-gradient(circle, ${r.goldPrimary} 0%, transparent 70%)`,animation:"pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite"}}),e.jsx("div",{className:"absolute bottom-1/4 -right-32 w-96 h-96 rounded-full opacity-5 blur-3xl",style:{background:`radial-gradient(circle, ${r.goldLight} 0%, transparent 70%)`,animation:"pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite 2s"}}),e.jsxs("div",{className:"flex mb-10 relative",style:{animation:"tissueLogoEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards",opacity:0},children:[e.jsx("div",{className:"absolute inset-0 blur-2xl opacity-40",style:{background:`radial-gradient(circle, ${r.goldPrimary} 0%, transparent 70%)`}}),e.jsx("img",{className:"h-20 relative z-10",src:u,alt:"TISSUE+",style:{filter:`drop-shadow(0 0 20px ${r.rgba("gold",.3)})`}})]}),e.jsxs("div",{className:"w-[380px] relative",style:{animation:"tissueCardEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards",opacity:0},children:[e.jsxs("div",{className:"p-8 rounded-2xl relative overflow-hidden",style:{background:r.rgba("black",.6),backdropFilter:"blur(40px) saturate(180%)",WebkitBackdropFilter:"blur(40px) saturate(180%)",border:`1px solid ${r.borderPrimary}`,boxShadow:`0 8px 32px ${r.rgba("black",.4)}, inset 0 1px 0 ${r.rgba("white",.05)}`},children:[e.jsx("div",{className:"absolute top-0 left-0 right-0 h-px",style:{background:`linear-gradient(90deg, transparent 0%, ${r.rgba("gold",.3)} 50%, transparent 100%)`}}),e.jsxs(o,{size:"large",form:s,onFinish:t=>l(t),style:{"--ant-color-bg-container":r.bgContainer,"--ant-color-border":r.borderPrimary,"--ant-color-primary":r.goldPrimary,"--ant-color-text":r.textPrimary,"--ant-color-text-placeholder":r.textTertiary},children:[e.jsx(o.Item,{name:"username",children:e.jsx(n,{prefix:e.jsx(b,{style:{color:r.textTertiary,fontSize:"16px"}}),placeholder:"用户名",style:{height:"48px",backgroundColor:r.bgElevated,border:`1px solid ${r.borderPrimary}`,borderRadius:"10px",color:r.textPrimary,fontSize:"15px",transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)"},onFocus:t=>{t.target.style.backgroundColor=r.bgContainer,t.target.style.borderColor=r.goldPrimary,t.target.style.boxShadow=`0 0 0 2px ${r.rgba("gold",.1)}`},onBlur:t=>{t.target.style.backgroundColor=r.bgElevated,t.target.style.borderColor=r.borderPrimary,t.target.style.boxShadow="none"}})}),e.jsx(o.Item,{name:"password",children:e.jsx(n.Password,{prefix:e.jsx(x,{style:{color:r.textTertiary,fontSize:"16px"}}),placeholder:"密码",style:{height:"48px",backgroundColor:r.bgElevated,border:`1px solid ${r.borderPrimary}`,borderRadius:"10px",color:r.textPrimary,fontSize:"15px",transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)"},onFocus:t=>{t.target.parentElement.style.backgroundColor=r.bgContainer,t.target.parentElement.style.borderColor=r.goldPrimary,t.target.parentElement.style.boxShadow=`0 0 0 2px ${r.rgba("gold",.1)}`},onBlur:t=>{t.target.parentElement.style.backgroundColor=r.bgElevated,t.target.parentElement.style.borderColor=r.borderPrimary,t.target.parentElement.style.boxShadow="none"}})}),e.jsx(o.Item,{noStyle:!0,name:"remember",valuePropName:"checked",children:e.jsx(g,{style:{marginBottom:24,color:r.textSecondary,fontSize:"14px"},children:"保持登录"})}),e.jsx(m,{type:"primary",htmlType:"submit",loading:a,style:{width:"100%",height:"48px",background:r.goldGradient,border:"none",borderRadius:"10px",fontSize:"16px",fontWeight:600,color:r.bgBase,boxShadow:`0 4px 16px ${r.rgba("gold",.25)}`,transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",cursor:a?"not-allowed":"pointer"},onMouseEnter:t=>{a||(t.currentTarget.style.background=r.goldGradientHover,t.currentTarget.style.boxShadow=`0 0 24px ${r.rgba("gold",.4)}, 0 8px 24px ${r.rgba("black",.3)}`,t.currentTarget.style.transform="translateY(-2px)")},onMouseLeave:t=>{a||(t.currentTarget.style.background=r.goldGradient,t.currentTarget.style.boxShadow=`0 4px 16px ${r.rgba("gold",.25)}`,t.currentTarget.style.transform="translateY(0)")},onMouseDown:t=>{a||(t.currentTarget.style.transform="translateY(0) scale(0.98)")},onMouseUp:t=>{a||(t.currentTarget.style.transform="translateY(-2px) scale(1)")},children:a?"登录中...":"登录"})]})]}),e.jsx("div",{className:"absolute -bottom-10 left-1/2 -translate-x-1/2 w-3/4 h-20 blur-3xl opacity-20 pointer-events-none",style:{background:`radial-gradient(ellipse, ${r.goldPrimary} 0%, transparent 70%)`}})]}),e.jsx("div",{className:"absolute bottom-8 text-center",style:{color:r.textTertiary,fontSize:"13px",animation:"tissueFadeIn 1s ease-out 0.4s forwards",opacity:0},children:e.jsx("div",{children:"TISSUE+ · 暗黑电影美学"})}),e.jsx("style",{children:`
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
                    background-color: ${r.bgElevated} !important;
                    border: 1px solid ${r.borderPrimary} !important;
                    color: ${r.textPrimary} !important;
                }

                .ant-input::placeholder,
                .ant-input-password input::placeholder {
                    color: ${r.textTertiary} !important;
                }

                .ant-input:focus,
                .ant-input-password:focus,
                .ant-input-password-focused,
                .ant-input:hover,
                .ant-input-password:hover {
                    background-color: ${r.bgContainer} !important;
                    border-color: ${r.goldPrimary} !important;
                    box-shadow: 0 0 0 2px ${r.rgba("gold",.1)} !important;
                }

                .ant-input-password .ant-input {
                    background-color: transparent !important;
                    border: none !important;
                }

                .ant-input-suffix {
                    color: ${r.textTertiary} !important;
                }

                .ant-checkbox-wrapper {
                    color: ${r.textSecondary} !important;
                }

                .ant-checkbox-inner {
                    background-color: ${r.bgElevated} !important;
                    border-color: ${r.borderPrimary} !important;
                }

                .ant-checkbox-checked .ant-checkbox-inner {
                    background-color: ${r.goldPrimary} !important;
                    border-color: ${r.goldPrimary} !important;
                }

                .ant-checkbox:hover .ant-checkbox-inner {
                    border-color: ${r.goldPrimary} !important;
                }

                .ant-form-item {
                    margin-bottom: 20px;
                }

                .ant-form-item-explain-error {
                    color: ${r.error} !important;
                    font-size: 13px;
                    margin-top: 4px;
                }
            `})]})}export{k as component};
