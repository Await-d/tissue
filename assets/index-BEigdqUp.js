import{aG as K,aB as J,aH as i,r as $,aI as z,aJ as P,aK as T,aL as G,aM as W,as as h,a3 as Q,ac as sr,W as X,F as e,av as Z,R as ir,G as L,at as j,O as dr,ag as H,am as lr,aN as ur,aO as cr,a7 as fr,aP as mr,U as br}from"./index-CyNTvvQc.js";import{M as pr}from"./index-DKvgVHxe.js";import{I as gr}from"./index-B8zg5PaH.js";var hr=function(d,a){var u;a===void 0&&(a={});var r=a.defaultPageSize,b=r===void 0?10:r,t=a.defaultCurrent,s=t===void 0?1:t,p=K(a,["defaultPageSize","defaultCurrent"]),c=J(d,i({defaultParams:[{current:s,pageSize:b}],refreshDepsAction:function(){F(1)}},p)),x=c.params[0]||{},_=x.current,D=_===void 0?1:_,v=x.pageSize,w=v===void 0?b:v,f=((u=c.data)===null||u===void 0?void 0:u.total)||0,q=$.useMemo(function(){return Math.ceil(f/w)},[w,f]),g=function(y,I){var M=y<=0?1:y,m=I<=0?1:I,A=Math.ceil(f/m);M>A&&(M=Math.max(1,A));var R=P(c.params||[]),C=R[0],E=C===void 0?{}:C,Y=R.slice(1);c.run.apply(c,T([],P(T([i(i({},E),{current:M,pageSize:m})],P(Y),!1)),!1))},F=function(y){g(y,w)},S=function(y){g(D,y)};return i(i({},c),{pagination:{current:D,pageSize:w,total:f,totalPage:q,onChange:z(g),changeCurrent:z(F),changePageSize:z(S)}})},xr=function(d,a){var u;a===void 0&&(a={});var r=a.form,b=a.defaultType,t=b===void 0?"simple":b,s=a.defaultParams,p=a.manual,c=p===void 0?!1:p,x=a.refreshDeps,_=x===void 0?[]:x,D=a.ready,v=D===void 0?!0:D,w=K(a,["form","defaultType","defaultParams","manual","refreshDeps","ready"]),f=hr(d,i(i({ready:v,manual:!0},w),{onSuccess:function(){for(var n,o=[],l=0;l<arguments.length;l++)o[l]=arguments[l];R.current=!0,(n=w.onSuccess)===null||n===void 0||n.call.apply(n,T([w],P(o),!1))}})),q=f.params,g=q===void 0?[]:q,F=f.run,S=g[2]||{},y=P($.useState((S==null?void 0:S.type)||t),2),I=y[0],M=y[1],m=$.useRef({}),A=$.useRef([]),R=$.useRef(!1),C=!!(r!=null&&r.getInternalHooks),E=function(){if(!r)return{};if(C)return r.getFieldsValue(null,function(){return!0});var n=r.getFieldsValue(),o={};return Object.keys(n).forEach(function(l){(!r.getFieldInstance||r.getFieldInstance(l))&&(o[l]=n[l])}),o},Y=function(){if(!r)return Promise.resolve({});var n=E(),o=Object.keys(n);return C?r.validateFields(o):new Promise(function(l,k){r.validateFields(o,function(V,N){V?k(V):l(N)})})},U=function(){if(r){if(C)return r.setFieldsValue(m.current);var n={};Object.keys(m.current).forEach(function(o){(!r.getFieldInstance||r.getFieldInstance(o))&&(n[o]=m.current[o])}),r.setFieldsValue(n)}},er=function(){var n=E();m.current=i(i({},m.current),n),M(function(o){return o==="simple"?"advance":"simple"})},B=function(n){v&&setTimeout(function(){Y().then(function(o){o===void 0&&(o={});var l=n||i(i({pageSize:a.defaultPageSize||10},(g==null?void 0:g[0])||{}),{current:1});if(!r){F(l);return}m.current=i(i({},m.current),o),F(l,o,{allFormData:m.current,type:I})}).catch(function(o){return o})})},ar=function(){var n,o;r&&r.resetFields(),B(i(i({},(s==null?void 0:s[0])||{}),{pageSize:a.defaultPageSize||((o=(n=a.defaultParams)===null||n===void 0?void 0:n[0])===null||o===void 0?void 0:o.pageSize)||10,current:1}))},tr=function(n){var o,l,k;(o=n==null?void 0:n.preventDefault)===null||o===void 0||o.call(n),B(R.current?void 0:i({pageSize:a.defaultPageSize||((k=(l=a.defaultParams)===null||l===void 0?void 0:l[0])===null||k===void 0?void 0:k.pageSize)||10,current:1},(s==null?void 0:s[0])||{}))},or=function(n,o,l,k){var V=P(g||[]),N=V[0],nr=V.slice(1);F.apply(void 0,T([i(i({},N),{current:n.current,pageSize:n.pageSize,filters:o,sorter:l,extra:k})],P(nr),!1))};$.useEffect(function(){if(g.length>0){m.current=(S==null?void 0:S.allFormData)||{},U(),F.apply(void 0,T([],P(g),!1));return}v&&(m.current=(s==null?void 0:s[1])||{},U(),c||B(s==null?void 0:s[0]))},[]),G(function(){v&&U()},[I]);var O=$.useRef(!1);return O.current=!1,G(function(){!c&&v&&(O.current=!0,r&&r.resetFields(),m.current=(s==null?void 0:s[1])||{},U(),B(s==null?void 0:s[0]))},[v]),G(function(){O.current||v&&(c||(O.current=!0,a.refreshDepsAction?a.refreshDepsAction():f.pagination.changeCurrent(1)))},T([],P(_),!1)),i(i({},f),{tableProps:{dataSource:((u=f.data)===null||u===void 0?void 0:u.list)||A.current,loading:f.loading,onChange:z(or),pagination:{current:f.pagination.current,pageSize:f.pagination.pageSize,total:f.pagination.total}},search:{submit:z(tr),type:I,changeType:z(er),reset:z(ar)}})};async function vr(d,a){return{list:(await W.request({url:"/user/list",method:"get",params:{...d,...a}})).data.data,total:0}}function rr(d){return W.request({url:"/user/",method:d.id?"put":"post",data:d})}function yr(){const[d]=h.useForm(),{userInfo:a}=Q(p=>p.auth),{getInfo:u}=sr().auth,r=X(),{run:b,loading:t}=J(rr,{manual:!0,onSuccess:()=>{u(),H.success("保存成功")}});$.useEffect(()=>{a&&d.setFieldsValue(a)},[a]);function s(p){if(p.password&&p.password!==p.confirmPassword)return H.error("两次输入密码不一致");b({...p,id:a.id})}return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
                .user-info-card .ant-card {
                    background: ${r.bgContainer};
                    border: 1px solid ${r.borderPrimary};
                    box-shadow: ${r.shadowSm};
                }

                .user-info-card .ant-card-head {
                    background: ${r.bgSpotlight};
                    border-bottom: 1px solid ${r.borderPrimary};
                }

                .user-info-card .ant-card-head-title {
                    color: ${r.textPrimary};
                    font-weight: 600;
                }

                .user-info-card .ant-form-item-label > label {
                    color: ${r.textPrimary};
                    font-weight: 500;
                }

                .user-info-card .ant-input,
                .user-info-card .ant-input-password {
                    background: ${r.bgElevated};
                    border: 1px solid ${r.borderPrimary};
                    color: ${r.textPrimary};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-input:hover,
                .user-info-card .ant-input-password:hover {
                    border-color: ${r.rgba("gold",.4)};
                }

                .user-info-card .ant-input:focus,
                .user-info-card .ant-input-password:focus,
                .user-info-card .ant-input-focused {
                    border-color: ${r.goldPrimary};
                    box-shadow: 0 0 0 2px ${r.rgba("gold",.15)};
                }

                .user-info-card .ant-input::placeholder {
                    color: ${r.textTertiary};
                }

                .user-info-card .ant-input-password .ant-input {
                    background: transparent;
                    border: none;
                }

                .user-info-card .ant-input-suffix {
                    color: ${r.textSecondary};
                }

                .user-info-card .ant-btn-primary {
                    background: ${r.goldPrimary};
                    border-color: ${r.goldPrimary};
                    color: ${r.bgBase};
                    font-weight: 600;
                    height: 40px;
                    padding: 0 32px;
                    box-shadow: ${r.shadowGold};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-btn-primary:hover {
                    background: ${r.goldLight} !important;
                    border-color: ${r.goldLight} !important;
                    box-shadow: 0 4px 12px ${r.rgba("gold",.4)} !important;
                    transform: translateY(-2px);
                }

                .user-info-card .ant-btn-primary:active {
                    transform: translateY(0);
                }

                .user-info-card .ant-form-item-explain-error {
                    color: ${r.error};
                }
            `}),e.jsx(Z,{title:"用户信息",className:"user-info-card",style:{background:r.bgContainer,border:`1px solid ${r.borderPrimary}`,boxShadow:r.shadowSm},styles:{header:{background:r.bgSpotlight,borderBottom:`1px solid ${r.borderPrimary}`,color:r.textPrimary}},children:e.jsxs(h,{form:d,layout:"vertical",onFinish:s,children:[e.jsxs(ir,{gutter:20,children:[e.jsx(L,{span:24,lg:12,children:e.jsx(h.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:e.jsx(j,{})})}),e.jsxs(L,{span:24,lg:12,children:[e.jsx(h.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:e.jsx(j,{})})," "]}),e.jsxs(L,{span:24,lg:12,children:[e.jsx(h.Item,{name:"password",label:"新密码",children:e.jsx(j.Password,{})})," "]}),e.jsx(L,{span:24,lg:12,children:e.jsx(h.Item,{name:"confirmPassword",label:"确认新密码",children:e.jsx(j.Password,{})})})]}),e.jsx(dr,{type:"primary",htmlType:"submit",loading:t,children:"保存"})]})})]})}function Pr(d){const{form:a,initValues:u,...r}=d,b=u==null?void 0:u.id;return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
                .user-modal .ant-modal-content {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(20px);
                }

                .user-modal .ant-modal-header {
                    background: transparent;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-modal .ant-modal-title {
                    color: #f0f0f2;
                    font-weight: 600;
                    font-size: 16px;
                }

                .user-modal .ant-modal-close {
                    color: #a0a0a8;
                }

                .user-modal .ant-modal-close:hover {
                    color: #f0f0f2;
                    background: rgba(255, 255, 255, 0.08);
                }

                .user-modal .ant-form-item-label > label {
                    color: #f0f0f2;
                    font-weight: 500;
                }

                .user-modal .ant-input,
                .user-modal .ant-input-password {
                    background: #141416 !important;
                    border: 1px solid rgba(255, 255, 255, 0.12) !important;
                    color: #f0f0f2 !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-modal .ant-input:hover,
                .user-modal .ant-input-password:hover {
                    border-color: rgba(212, 168, 82, 0.4) !important;
                }

                .user-modal .ant-input:focus,
                .user-modal .ant-input-password:focus,
                .user-modal .ant-input-focused {
                    border-color: #d4a852 !important;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.15) !important;
                }

                .user-modal .ant-input::placeholder {
                    color: #6a6a72;
                }

                .user-modal .ant-input-password .ant-input {
                    background: transparent !important;
                    border: none !important;
                }

                .user-modal .ant-input-suffix {
                    color: #a0a0a8;
                }

                .user-modal .ant-modal-footer {
                    border-top: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-modal .ant-btn-primary {
                    background: #d4a852;
                    border-color: #d4a852;
                    color: #0d0d0f;
                    font-weight: 600;
                    box-shadow: 0 2px 8px rgba(212, 168, 82, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-modal .ant-btn-primary:hover {
                    background: #e8c780 !important;
                    border-color: #e8c780 !important;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4) !important;
                    transform: translateY(-1px);
                }

                .user-modal .ant-btn-default {
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #a0a0a8;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-modal .ant-btn-default:hover {
                    border-color: rgba(255, 255, 255, 0.2) !important;
                    color: #f0f0f2 !important;
                    background: rgba(255, 255, 255, 0.05) !important;
                }

                .user-modal .ant-form-item-explain-error {
                    color: #ff4d4f;
                }
            `}),e.jsx(lr,{title:b?"编辑用户":"新建用户",...r,className:"user-modal",children:e.jsxs(h,{layout:"vertical",form:a,children:[e.jsx(h.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:e.jsx(j,{})}),e.jsx(h.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:e.jsx(j,{})}),e.jsx(h.Item,{name:"password",label:"新密码",rules:[{required:!b}],children:e.jsx(j.Password,{})}),e.jsx(h.Item,{name:"confirmPassword",label:"确认新密码",rules:[{required:!b}],children:e.jsx(j.Password,{})})]})})]})}function wr(){const{message:d}=ur.useApp(),{tableProps:a,refresh:u}=xr(vr),{setOpen:r,modalProps:b}=cr({service:rr,onOk:()=>{d.success("保存成功"),r(!1),u()}}),t=X(),s=[{title:"名称",dataIndex:"name"},{title:"用户名",dataIndex:"username"},{title:"管理员",dataIndex:"is_admin",render:c=>c?"是":"否"},{title:"",dataIndex:"operations",width:20,render:(c,x)=>!x.is_admin&&e.jsx(pr,{onClick:_=>p(_,x)})}];function p(c,x){c==="edit"&&r(!0,x)}return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
                .user-list-card .ant-card {
                    background: ${t.bgContainer};
                    border: 1px solid ${t.borderPrimary};
                    box-shadow: ${t.shadowSm};
                }

                .user-list-card .ant-card-head {
                    background: ${t.bgSpotlight};
                    border-bottom: 1px solid ${t.borderPrimary};
                }

                .user-list-card .ant-card-head-title {
                    color: ${t.textPrimary};
                    font-weight: 600;
                }

                .user-list-card .ant-card-extra {
                    padding: 0;
                }

                .user-list-card .ant-table {
                    background: transparent;
                }

                .user-list-card .ant-table-thead > tr > th {
                    background: ${t.bgSpotlight};
                    border-bottom: 1px solid ${t.borderPrimary};
                    color: ${t.textPrimary};
                    font-weight: 600;
                    padding: 16px;
                }

                .user-list-card .ant-table-tbody > tr {
                    background: transparent;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-list-card .ant-table-tbody > tr > td {
                    border-bottom: 1px solid ${t.borderSecondary};
                    color: ${t.textSecondary};
                    padding: 16px;
                }

                .user-list-card .ant-table-tbody > tr:hover {
                    background: ${t.rgba("gold",.08)} !important;
                }

                .user-list-card .ant-table-tbody > tr:hover > td {
                    color: ${t.textPrimary};
                    border-bottom-color: ${t.rgba("gold",.15)};
                }

                .user-list-card .ant-table-tbody > tr:last-child > td {
                    border-bottom: none;
                }

                .user-list-card .icon-button {
                    width: 32px;
                    height: 32px;
                    border-radius: 6px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: ${t.goldPrimary};
                    color: ${t.bgBase};
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 2px 6px ${t.rgba("gold",.3)};
                }

                .user-list-card .icon-button:hover {
                    background: ${t.goldLight};
                    box-shadow: 0 4px 12px ${t.rgba("gold",.4)};
                    transform: translateY(-2px);
                }

                .user-list-card .icon-button:active {
                    transform: translateY(0);
                }

                .user-list-card .ant-table-placeholder .ant-table-cell {
                    background: transparent;
                    border: none;
                }

                .user-list-card .ant-empty-description {
                    color: ${t.textTertiary};
                }
            `}),e.jsxs(Z,{title:"用户管理",extra:e.jsx(gr,{onClick:()=>r(!0),children:e.jsx(mr,{})}),className:"user-list-card",style:{background:t.bgContainer,border:`1px solid ${t.borderPrimary}`,boxShadow:t.shadowSm},styles:{header:{background:t.bgSpotlight,borderBottom:`1px solid ${t.borderPrimary}`,color:t.textPrimary},body:{padding:0}},children:[e.jsx(fr,{rowKey:"id",columns:s,...a,pagination:!1}),e.jsx(Pr,{...b})]})]})}function Fr(){const{userInfo:d}=Q(a=>a.auth);return e.jsxs(br,{direction:"vertical",style:{width:"100%"},children:[e.jsx(yr,{}),(d==null?void 0:d.is_admin)&&e.jsx(wr,{})]})}export{Fr as component};
