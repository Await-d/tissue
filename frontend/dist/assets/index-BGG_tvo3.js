import{aI as H,aC as J,aJ as l,r as j,aK as I,aL as P,aM as T,aN as G,aO as Q,as as h,a3 as W,ac as sr,W as X,F as e,av as Z,R as ir,G as L,at as F,O as dr,ag as K,am as lr,aP as ur,aQ as cr,a7 as fr,aR as mr,U as gr}from"./index-BqYHbufV.js";import{M as pr}from"./index-BCCE0lU0.js";import{I as br}from"./index-D_ZGMix8.js";var vr=function(i,a){var d;a===void 0&&(a={});var r=a.defaultPageSize,p=r===void 0?10:r,t=a.defaultCurrent,s=t===void 0?1:t,f=H(a,["defaultPageSize","defaultCurrent"]),c=J(i,l({defaultParams:[{current:s,pageSize:p}],refreshDepsAction:function(){_(1)}},f)),b=c.params[0]||{},w=b.current,R=w===void 0?1:w,x=b.pageSize,S=x===void 0?p:x,m=((d=c.data)===null||d===void 0?void 0:d.total)||0,V=j.useMemo(function(){return Math.ceil(m/S)},[S,m]),v=function(y,k){var D=y<=0?1:y,g=k<=0?1:k,q=Math.ceil(m/g);D>q&&(D=Math.max(1,q));var M=P(c.params||[]),C=M[0],E=C===void 0?{}:C,Y=M.slice(1);c.run.apply(c,T([],P(T([l(l({},E),{current:D,pageSize:g})],P(Y),!1)),!1))},_=function(y){v(y,S)},$=function(y){v(R,y)};return l(l({},c),{pagination:{current:R,pageSize:S,total:m,totalPage:V,onChange:I(v),changeCurrent:I(_),changePageSize:I($)}})},hr=function(i,a){var d;a===void 0&&(a={});var r=a.form,p=a.defaultType,t=p===void 0?"simple":p,s=a.defaultParams,f=a.manual,c=f===void 0?!1:f,b=a.refreshDeps,w=b===void 0?[]:b,R=a.ready,x=R===void 0?!0:R,S=H(a,["form","defaultType","defaultParams","manual","refreshDeps","ready"]),m=vr(i,l(l({ready:x,manual:!0},S),{onSuccess:function(){for(var o,n=[],u=0;u<arguments.length;u++)n[u]=arguments[u];M.current=!0,(o=S.onSuccess)===null||o===void 0||o.call.apply(o,T([S],P(n),!1))}})),V=m.params,v=V===void 0?[]:V,_=m.run,$=v[2]||{},y=P(j.useState(($==null?void 0:$.type)||t),2),k=y[0],D=y[1],g=j.useRef({}),q=j.useRef([]),M=j.useRef(!1),C=!!(r!=null&&r.getInternalHooks),E=function(){if(!r)return{};if(C)return r.getFieldsValue(null,function(){return!0});var o=r.getFieldsValue(),n={};return Object.keys(o).forEach(function(u){(!r.getFieldInstance||r.getFieldInstance(u))&&(n[u]=o[u])}),n},Y=function(){if(!r)return Promise.resolve({});var o=E(),n=Object.keys(o);return C?r.validateFields(n):new Promise(function(u,z){r.validateFields(n,function(A,N){A?z(A):u(N)})})},U=function(){if(r){if(C)return r.setFieldsValue(g.current);var o={};Object.keys(g.current).forEach(function(n){(!r.getFieldInstance||r.getFieldInstance(n))&&(o[n]=g.current[n])}),r.setFieldsValue(o)}},er=function(){var o=E();g.current=l(l({},g.current),o),D(function(n){return n==="simple"?"advance":"simple"})},O=function(o){x&&setTimeout(function(){Y().then(function(n){n===void 0&&(n={});var u=o||l(l({pageSize:a.defaultPageSize||10},(v==null?void 0:v[0])||{}),{current:1});if(!r){_(u);return}g.current=l(l({},g.current),n),_(u,n,{allFormData:g.current,type:k})}).catch(function(n){return n})})},ar=function(){var o,n;r&&r.resetFields(),O(l(l({},(s==null?void 0:s[0])||{}),{pageSize:a.defaultPageSize||((n=(o=a.defaultParams)===null||o===void 0?void 0:o[0])===null||n===void 0?void 0:n.pageSize)||10,current:1}))},tr=function(o){var n,u,z;(n=o==null?void 0:o.preventDefault)===null||n===void 0||n.call(o),O(M.current?void 0:l({pageSize:a.defaultPageSize||((z=(u=a.defaultParams)===null||u===void 0?void 0:u[0])===null||z===void 0?void 0:z.pageSize)||10,current:1},(s==null?void 0:s[0])||{}))},nr=function(o,n,u,z){var A=P(v||[]),N=A[0],or=A.slice(1);_.apply(void 0,T([l(l({},N),{current:o.current,pageSize:o.pageSize,filters:n,sorter:u,extra:z})],P(or),!1))};j.useEffect(function(){if(v.length>0){g.current=($==null?void 0:$.allFormData)||{},U(),_.apply(void 0,T([],P(v),!1));return}x&&(g.current=(s==null?void 0:s[1])||{},U(),c||O(s==null?void 0:s[0]))},[]),G(function(){x&&U()},[k]);var B=j.useRef(!1);return B.current=!1,G(function(){!c&&x&&(B.current=!0,r&&r.resetFields(),g.current=(s==null?void 0:s[1])||{},U(),O(s==null?void 0:s[0]))},[x]),G(function(){B.current||x&&(c||(B.current=!0,a.refreshDepsAction?a.refreshDepsAction():m.pagination.changeCurrent(1)))},T([],P(w),!1)),l(l({},m),{tableProps:{dataSource:((d=m.data)===null||d===void 0?void 0:d.list)||q.current,loading:m.loading,onChange:I(nr),pagination:{current:m.pagination.current,pageSize:m.pagination.pageSize,total:m.pagination.total}},search:{submit:I(tr),type:k,changeType:I(er),reset:I(ar)}})};async function xr(i,a){let d=await Q.request({url:"/user/list",method:"get",params:{...i,...a}});return{list:d.data,total:d.total??(Array.isArray(d.data)?d.data.length:0)}}function rr(i){return Q.request({url:"/user/",method:i.id?"put":"post",data:i})}function yr(){const[i]=h.useForm(),{userInfo:a}=W(f=>f.auth),{getInfo:d}=sr().auth,r=X(),{run:p,loading:t}=J(rr,{manual:!0,onSuccess:()=>{d(),K.success("保存成功"),i.resetFields(["password","confirmPassword"])}});j.useEffect(()=>{a&&i.setFieldsValue(a)},[a,i]);function s(f){if(!a){K.error("用户信息未加载");return}if(f.password&&f.password!==f.confirmPassword)return K.error("两次输入密码不一致");p({...f,id:a.id})}return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
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
            `}),e.jsx(Z,{title:"用户信息",className:"user-info-card",style:{background:r.bgContainer,border:`1px solid ${r.borderPrimary}`,boxShadow:r.shadowSm},styles:{header:{background:r.bgSpotlight,borderBottom:`1px solid ${r.borderPrimary}`,color:r.textPrimary}},children:e.jsxs(h,{form:i,layout:"vertical",onFinish:s,children:[e.jsxs(ir,{gutter:20,children:[e.jsx(L,{span:24,lg:12,children:e.jsx(h.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:e.jsx(F,{})})}),e.jsxs(L,{span:24,lg:12,children:[e.jsx(h.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:e.jsx(F,{})})," "]}),e.jsxs(L,{span:24,lg:12,children:[e.jsx(h.Item,{name:"password",label:"新密码",children:e.jsx(F.Password,{})})," "]}),e.jsx(L,{span:24,lg:12,children:e.jsx(h.Item,{name:"confirmPassword",label:"确认新密码",children:e.jsx(F.Password,{})})})]}),e.jsx(dr,{type:"primary",htmlType:"submit",loading:t,children:"保存"})]})})]})}function Pr(i){const{form:a,initValues:d,...r}=i,p=d==null?void 0:d.id;return e.jsx(lr,{title:p?"编辑用户":"新建用户",...r,children:e.jsxs(h,{layout:"vertical",form:a,children:[e.jsx(h.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:e.jsx(F,{})}),e.jsx(h.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:e.jsx(F,{})}),e.jsx(h.Item,{name:"password",label:"新密码",rules:[{required:!p,message:"请输入密码"}],children:e.jsx(F.Password,{})}),e.jsx(h.Item,{name:"confirmPassword",label:"确认新密码",dependencies:["password"],rules:[{required:!p,message:"请再次输入密码"},({getFieldValue:t})=>({validator(s,f){return!f||t("password")===f?Promise.resolve():Promise.reject(new Error("两次输入的密码不一致"))}})],children:e.jsx(F.Password,{})})]})})}function wr(){const{message:i}=ur.useApp(),{tableProps:a,refresh:d}=hr(xr),{setOpen:r,modalProps:p}=cr({service:rr,transform:c=>{const{confirmPassword:b,...w}=c;return w},onOk:()=>{i.success("保存成功"),r(!1),d()}}),t=X(),s=[{title:"名称",dataIndex:"name"},{title:"用户名",dataIndex:"username"},{title:"管理员",dataIndex:"is_admin",render:c=>c?"是":"否"},{title:"",dataIndex:"operations",width:20,render:(c,b)=>!b.is_admin&&e.jsx(pr,{onClick:w=>f(w,b)})}];function f(c,b){c==="edit"&&r(!0,b)}return e.jsxs(e.Fragment,{children:[e.jsx("style",{children:`
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
            `}),e.jsxs(Z,{title:"用户管理",extra:e.jsx(br,{onClick:()=>r(!0),children:e.jsx(mr,{})}),className:"user-list-card",style:{background:t.bgContainer,border:`1px solid ${t.borderPrimary}`,boxShadow:t.shadowSm},styles:{header:{background:t.bgSpotlight,borderBottom:`1px solid ${t.borderPrimary}`,color:t.textPrimary},body:{padding:0}},children:[e.jsx(fr,{rowKey:"id",columns:s,...a,pagination:!1}),e.jsx(Pr,{...p})]})]})}function Fr(){const{userInfo:i}=W(a=>a.auth);return e.jsxs(gr,{direction:"vertical",style:{width:"100%"},children:[e.jsx(yr,{}),(i==null?void 0:i.is_admin)&&e.jsx(wr,{})]})}export{Fr as component};
