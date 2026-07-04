import{aH as K,aB as J,aI as s,r as j,aJ as z,aK as P,aL as T,aM as G,aN as Q,as as v,a3 as W,ac as ir,W as X,F as e,av as Z,R as sr,G as L,at as w,O as dr,ag as H,am as lr,aO as ur,aP as cr,a7 as fr,aQ as gr,U as mr}from"./index-B5NBX6Vt.js";import{M as br}from"./index-BO-p4JVH.js";import{I as pr}from"./index-BGCcJlDE.js";var vr=function(d,a){var u;a===void 0&&(a={});var r=a.defaultPageSize,m=r===void 0?10:r,t=a.defaultCurrent,i=t===void 0?1:t,b=K(a,["defaultPageSize","defaultCurrent"]),c=J(d,s({defaultParams:[{current:i,pageSize:m}],refreshDepsAction:function(){F(1)}},b)),h=c.params[0]||{},I=h.current,D=I===void 0?1:I,x=h.pageSize,S=x===void 0?m:x,f=((u=c.data)===null||u===void 0?void 0:u.total)||0,q=j.useMemo(function(){return Math.ceil(f/S)},[S,f]),p=function(y,k){var M=y<=0?1:y,g=k<=0?1:k,A=Math.ceil(f/g);M>A&&(M=Math.max(1,A));var R=P(c.params||[]),C=R[0],E=C===void 0?{}:C,Y=R.slice(1);c.run.apply(c,T([],P(T([s(s({},E),{current:M,pageSize:g})],P(Y),!1)),!1))},F=function(y){p(y,S)},$=function(y){p(D,y)};return s(s({},c),{pagination:{current:D,pageSize:S,total:f,totalPage:q,onChange:z(p),changeCurrent:z(F),changePageSize:z($)}})},hr=function(d,a){var u;a===void 0&&(a={});var r=a.form,m=a.defaultType,t=m===void 0?"simple":m,i=a.defaultParams,b=a.manual,c=b===void 0?!1:b,h=a.refreshDeps,I=h===void 0?[]:h,D=a.ready,x=D===void 0?!0:D,S=K(a,["form","defaultType","defaultParams","manual","refreshDeps","ready"]),f=vr(d,s(s({ready:x,manual:!0},S),{onSuccess:function(){for(var o,n=[],l=0;l<arguments.length;l++)n[l]=arguments[l];R.current=!0,(o=S.onSuccess)===null||o===void 0||o.call.apply(o,T([S],P(n),!1))}})),q=f.params,p=q===void 0?[]:q,F=f.run,$=p[2]||{},y=P(j.useState(($==null?void 0:$.type)||t),2),k=y[0],M=y[1],g=j.useRef({}),A=j.useRef([]),R=j.useRef(!1),C=!!(r!=null&&r.getInternalHooks),E=function(){if(!r)return{};if(C)return r.getFieldsValue(null,function(){return!0});var o=r.getFieldsValue(),n={};return Object.keys(o).forEach(function(l){(!r.getFieldInstance||r.getFieldInstance(l))&&(n[l]=o[l])}),n},Y=function(){if(!r)return Promise.resolve({});var o=E(),n=Object.keys(o);return C?r.validateFields(n):new Promise(function(l,_){r.validateFields(n,function(V,N){V?_(V):l(N)})})},U=function(){if(r){if(C)return r.setFieldsValue(g.current);var o={};Object.keys(g.current).forEach(function(n){(!r.getFieldInstance||r.getFieldInstance(n))&&(o[n]=g.current[n])}),r.setFieldsValue(o)}},er=function(){var o=E();g.current=s(s({},g.current),o),M(function(n){return n==="simple"?"advance":"simple"})},B=function(o){x&&setTimeout(function(){Y().then(function(n){n===void 0&&(n={});var l=o||s(s({pageSize:a.defaultPageSize||10},(p==null?void 0:p[0])||{}),{current:1});if(!r){F(l);return}g.current=s(s({},g.current),n),F(l,n,{allFormData:g.current,type:k})}).catch(function(n){return n})})},ar=function(){var o,n;r&&r.resetFields(),B(s(s({},(i==null?void 0:i[0])||{}),{pageSize:a.defaultPageSize||((n=(o=a.defaultParams)===null||o===void 0?void 0:o[0])===null||n===void 0?void 0:n.pageSize)||10,current:1}))},tr=function(o){var n,l,_;(n=o==null?void 0:o.preventDefault)===null||n===void 0||n.call(o),B(R.current?void 0:s({pageSize:a.defaultPageSize||((_=(l=a.defaultParams)===null||l===void 0?void 0:l[0])===null||_===void 0?void 0:_.pageSize)||10,current:1},(i==null?void 0:i[0])||{}))},nr=function(o,n,l,_){var V=P(p||[]),N=V[0],or=V.slice(1);F.apply(void 0,T([s(s({},N),{current:o.current,pageSize:o.pageSize,filters:n,sorter:l,extra:_})],P(or),!1))};j.useEffect(function(){if(p.length>0){g.current=($==null?void 0:$.allFormData)||{},U(),F.apply(void 0,T([],P(p),!1));return}x&&(g.current=(i==null?void 0:i[1])||{},U(),c||B(i==null?void 0:i[0]))},[]),G(function(){x&&U()},[k]);var O=j.useRef(!1);return O.current=!1,G(function(){!c&&x&&(O.current=!0,r&&r.resetFields(),g.current=(i==null?void 0:i[1])||{},U(),B(i==null?void 0:i[0]))},[x]),G(function(){O.current||x&&(c||(O.current=!0,a.refreshDepsAction?a.refreshDepsAction():f.pagination.changeCurrent(1)))},T([],P(I),!1)),s(s({},f),{tableProps:{dataSource:((u=f.data)===null||u===void 0?void 0:u.list)||A.current,loading:f.loading,onChange:z(nr),pagination:{current:f.pagination.current,pageSize:f.pagination.pageSize,total:f.pagination.total}},search:{submit:z(tr),type:k,changeType:z(er),reset:z(ar)}})};async function xr(d,a){return{list:(await Q.request({url:"/user/list",method:"get",params:{...d,...a}})).data,total:0}}function rr(d){return Q.request({url:"/user/",method:d.id?"put":"post",data:d})}function yr(){const[d]=v.useForm(),{userInfo:a}=W(b=>b.auth),{getInfo:u}=ir().auth,r=X(),{run:m,loading:t}=J(rr,{manual:!0,onSuccess:()=>{u(),H.success("保存成功")}});j.useEffect(()=>{a&&d.setFieldsValue(a)},[a]);function i(b){if(b.password&&b.password!==b.confirmPassword)return H.error("两次输入密码不一致");m({...b,id:a.id})}return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
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
            `}),e.jsx(Z,{title:"用户信息",className:"user-info-card",style:{background:r.bgContainer,border:`1px solid ${r.borderPrimary}`,boxShadow:r.shadowSm},styles:{header:{background:r.bgSpotlight,borderBottom:`1px solid ${r.borderPrimary}`,color:r.textPrimary}},children:e.jsxs(v,{form:d,layout:"vertical",onFinish:i,children:[e.jsxs(sr,{gutter:20,children:[e.jsx(L,{span:24,lg:12,children:e.jsx(v.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:e.jsx(w,{})})}),e.jsxs(L,{span:24,lg:12,children:[e.jsx(v.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:e.jsx(w,{})})," "]}),e.jsxs(L,{span:24,lg:12,children:[e.jsx(v.Item,{name:"password",label:"新密码",children:e.jsx(w.Password,{})})," "]}),e.jsx(L,{span:24,lg:12,children:e.jsx(v.Item,{name:"confirmPassword",label:"确认新密码",children:e.jsx(w.Password,{})})})]}),e.jsx(dr,{type:"primary",htmlType:"submit",loading:t,children:"保存"})]})})]})}function Pr(d){const{form:a,initValues:u,...r}=d,m=u==null?void 0:u.id;return e.jsx(lr,{title:m?"编辑用户":"新建用户",...r,children:e.jsxs(v,{layout:"vertical",form:a,children:[e.jsx(v.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:e.jsx(w,{})}),e.jsx(v.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:e.jsx(w,{})}),e.jsx(v.Item,{name:"password",label:"新密码",rules:[{required:!m}],children:e.jsx(w.Password,{})}),e.jsx(v.Item,{name:"confirmPassword",label:"确认新密码",rules:[{required:!m}],children:e.jsx(w.Password,{})})]})})}function Sr(){const{message:d}=ur.useApp(),{tableProps:a,refresh:u}=hr(xr),{setOpen:r,modalProps:m}=cr({service:rr,onOk:()=>{d.success("保存成功"),r(!1),u()}}),t=X(),i=[{title:"名称",dataIndex:"name"},{title:"用户名",dataIndex:"username"},{title:"管理员",dataIndex:"is_admin",render:c=>c?"是":"否"},{title:"",dataIndex:"operations",width:20,render:(c,h)=>!h.is_admin&&e.jsx(br,{onClick:I=>b(I,h)})}];function b(c,h){c==="edit"&&r(!0,h)}return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
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
            `}),e.jsxs(Z,{title:"用户管理",extra:e.jsx(pr,{onClick:()=>r(!0),children:e.jsx(gr,{})}),className:"user-list-card",style:{background:t.bgContainer,border:`1px solid ${t.borderPrimary}`,boxShadow:t.shadowSm},styles:{header:{background:t.bgSpotlight,borderBottom:`1px solid ${t.borderPrimary}`,color:t.textPrimary},body:{padding:0}},children:[e.jsx(fr,{rowKey:"id",columns:i,...a,pagination:!1}),e.jsx(Pr,{...m})]})]})}function Fr(){const{userInfo:d}=W(a=>a.auth);return e.jsxs(mr,{direction:"vertical",style:{width:"100%"},children:[e.jsx(yr,{}),(d==null?void 0:d.is_admin)&&e.jsx(Sr,{})]})}export{Fr as component};
