import{as as o,a3 as l,ac as c,W as p,r as d,F as t,at as n,al as m,au as u,O as x}from"./index-zbzQnAx1.js";import{L as g}from"./logo-D6Xba1mH.js";import{R as b}from"./LockOutlined-DSgxE-oE.js";function k(){const[i]=o.useForm(),{logging:a}=l(e=>e.auth),{login:s}=c().auth,r=p();return d.useEffect(()=>{document.body.style.backgroundColor=r.bgBase},[r]),t.jsxs("div",{className:"h-dvh flex flex-col justify-center items-center relative overflow-hidden",style:{background:`linear-gradient(135deg, ${r.bgBase} 0%, ${r.bgElevated} 50%, ${r.bgBase} 100%)`},children:[t.jsx("div",{className:"absolute top-1/4 -left-32 w-96 h-96 rounded-full opacity-5 blur-3xl",style:{background:`radial-gradient(circle, ${r.goldPrimary} 0%, transparent 70%)`,animation:"pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite"}}),t.jsx("div",{className:"absolute bottom-1/4 -right-32 w-96 h-96 rounded-full opacity-5 blur-3xl",style:{background:`radial-gradient(circle, ${r.goldLight} 0%, transparent 70%)`,animation:"pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite 2s"}}),t.jsxs("div",{className:"flex mb-10 relative",style:{animation:"tissueLogoEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards",opacity:0},children:[t.jsx("div",{className:"absolute inset-0 blur-2xl opacity-40",style:{background:`radial-gradient(circle, ${r.goldPrimary} 0%, transparent 70%)`}}),t.jsx("img",{className:"h-20 relative z-10",src:g,alt:"TISSUE+",style:{filter:`drop-shadow(0 0 20px ${r.rgba("gold",.3)})`}})]}),t.jsxs("div",{className:"w-[380px] relative",style:{animation:"tissueCardEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards",opacity:0},children:[t.jsxs("div",{className:"p-8 rounded-2xl relative overflow-hidden",style:{background:r.rgba("black",.6),backdropFilter:"blur(40px) saturate(180%)",WebkitBackdropFilter:"blur(40px) saturate(180%)",border:`1px solid ${r.borderPrimary}`,boxShadow:`0 8px 32px ${r.rgba("black",.4)}, inset 0 1px 0 ${r.rgba("white",.05)}`},children:[t.jsx("div",{className:"absolute top-0 left-0 right-0 h-px",style:{background:`linear-gradient(90deg, transparent 0%, ${r.rgba("gold",.3)} 50%, transparent 100%)`}}),t.jsxs(o,{size:"large",form:i,onFinish:e=>s(e),style:{"--ant-color-bg-container":r.bgContainer,"--ant-color-border":r.borderPrimary,"--ant-color-primary":r.goldPrimary,"--ant-color-text":r.textPrimary,"--ant-color-text-placeholder":r.textTertiary},children:[t.jsx(o.Item,{name:"username",children:t.jsx(n,{prefix:t.jsx(m,{style:{color:r.textTertiary,fontSize:"16px"}}),placeholder:"用户名",className:"login-input"})}),t.jsx(o.Item,{name:"password",children:t.jsx(n.Password,{prefix:t.jsx(b,{style:{color:r.textTertiary,fontSize:"16px"}}),placeholder:"密码",className:"login-input"})}),t.jsx(o.Item,{noStyle:!0,name:"remember",valuePropName:"checked",children:t.jsx(u,{style:{marginBottom:24,color:r.textSecondary,fontSize:"14px"},children:"保持登录"})}),t.jsx(x,{type:"primary",htmlType:"submit",loading:a,style:{width:"100%",height:"48px",background:r.goldGradient,border:"none",borderRadius:"10px",fontSize:"16px",fontWeight:600,color:r.bgBase,boxShadow:`0 4px 16px ${r.rgba("gold",.25)}`,transition:"all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",cursor:a?"not-allowed":"pointer"},onMouseEnter:e=>{a||(e.currentTarget.style.background=r.goldGradientHover,e.currentTarget.style.boxShadow=`0 0 24px ${r.rgba("gold",.4)}, 0 8px 24px ${r.rgba("black",.3)}`,e.currentTarget.style.transform="translateY(-2px)")},onMouseLeave:e=>{a||(e.currentTarget.style.background=r.goldGradient,e.currentTarget.style.boxShadow=`0 4px 16px ${r.rgba("gold",.25)}`,e.currentTarget.style.transform="translateY(0)")},onMouseDown:e=>{a||(e.currentTarget.style.transform="translateY(0) scale(0.98)")},onMouseUp:e=>{a||(e.currentTarget.style.transform="translateY(-2px) scale(1)")},children:a?"登录中...":"登录"})]})]}),t.jsx("div",{className:"absolute -bottom-10 left-1/2 -translate-x-1/2 w-3/4 h-20 blur-3xl opacity-20 pointer-events-none",style:{background:`radial-gradient(ellipse, ${r.goldPrimary} 0%, transparent 70%)`}})]}),t.jsx("div",{className:"absolute bottom-8 text-center",style:{color:r.textTertiary,fontSize:"13px",animation:"tissueFadeIn 1s ease-out 0.4s forwards",opacity:0},children:t.jsx("div",{children:"TISSUE+ · 暗黑电影美学"})}),t.jsx("style",{children:`
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

                /* 登录页输入框统一样式 */
                .login-input,
                .login-input.ant-input-affix-wrapper {
                    height: 48px !important;
                    background-color: ${r.bgElevated} !important;
                    border: 1px solid ${r.borderPrimary} !important;
                    border-radius: 10px !important;
                    color: ${r.textPrimary} !important;
                    font-size: 15px !important;
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    padding: 0 11px !important;
                }

                .login-input:hover,
                .login-input.ant-input-affix-wrapper:hover {
                    background-color: ${r.bgContainer} !important;
                    border-color: ${r.goldPrimary} !important;
                }

                .login-input:focus,
                .login-input.ant-input-affix-wrapper-focused {
                    background-color: ${r.bgContainer} !important;
                    border-color: ${r.goldPrimary} !important;
                    box-shadow: 0 0 0 2px ${r.rgba("gold",.1)} !important;
                }

                .login-input input,
                .login-input.ant-input-affix-wrapper input {
                    background-color: transparent !important;
                    color: ${r.textPrimary} !important;
                    font-size: 15px !important;
                }

                .login-input input::placeholder,
                .login-input.ant-input-affix-wrapper input::placeholder {
                    color: ${r.textTertiary} !important;
                }

                .login-input .ant-input-suffix {
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
