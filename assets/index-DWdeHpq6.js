import{aF as J,aA as Q,aG as s,r as P,aH as z,aI as h,aJ as M,aK as K,aL as W,ar as m,a2 as X,ab as or,F as r,au as Z,R as sr,G as N,as as F,O as ir,af as L,al as dr,aM as lr,aN as ur,a6 as cr,aO as fr,U as pr}from"./index-CPAKaPzh.js";import{M as br}from"./index-CpM-Peu4.js";import{I as mr}from"./index-FEDTYq1f.js";var gr=function(i,a){var l;a===void 0&&(a={});var e=a.defaultPageSize,p=e===void 0?10:e,w=a.defaultCurrent,n=w===void 0?1:w,_=J(a,["defaultPageSize","defaultCurrent"]),u=Q(i,s({defaultParams:[{current:n,pageSize:p}],refreshDepsAction:function(){S(1)}},_)),g=u.params[0]||{},I=g.current,R=I===void 0?1:I,x=g.pageSize,y=x===void 0?p:x,c=((l=u.data)===null||l===void 0?void 0:l.total)||0,q=P.useMemo(function(){return Math.ceil(c/y)},[y,c]),b=function(v,C){var T=v<=0?1:v,f=C<=0?1:C,U=Math.ceil(c/f);T>U&&(T=Math.max(1,U));var A=h(u.params||[]),D=A[0],E=D===void 0?{}:D,G=A.slice(1);u.run.apply(u,M([],h(M([s(s({},E),{current:T,pageSize:f})],h(G),!1)),!1))},S=function(v){b(v,y)},j=function(v){b(R,v)};return s(s({},u),{pagination:{current:R,pageSize:y,total:c,totalPage:q,onChange:z(b),changeCurrent:z(S),changePageSize:z(j)}})},xr=function(i,a){var l;a===void 0&&(a={});var e=a.form,p=a.defaultType,w=p===void 0?"simple":p,n=a.defaultParams,_=a.manual,u=_===void 0?!1:_,g=a.refreshDeps,I=g===void 0?[]:g,R=a.ready,x=R===void 0?!0:R,y=J(a,["form","defaultType","defaultParams","manual","refreshDeps","ready"]),c=gr(i,s(s({ready:x,manual:!0},y),{onSuccess:function(){for(var o,t=[],d=0;d<arguments.length;d++)t[d]=arguments[d];A.current=!0,(o=y.onSuccess)===null||o===void 0||o.call.apply(o,M([y],h(t),!1))}})),q=c.params,b=q===void 0?[]:q,S=c.run,j=b[2]||{},v=h(P.useState((j==null?void 0:j.type)||w),2),C=v[0],T=v[1],f=P.useRef({}),U=P.useRef([]),A=P.useRef(!1),D=!!(e!=null&&e.getInternalHooks),E=function(){if(!e)return{};if(D)return e.getFieldsValue(null,function(){return!0});var o=e.getFieldsValue(),t={};return Object.keys(o).forEach(function(d){(!e.getFieldInstance||e.getFieldInstance(d))&&(t[d]=o[d])}),t},G=function(){if(!e)return Promise.resolve({});var o=E(),t=Object.keys(o);return D?e.validateFields(t):new Promise(function(d,k){e.validateFields(t,function(V,H){V?k(V):d(H)})})},O=function(){if(e){if(D)return e.setFieldsValue(f.current);var o={};Object.keys(f.current).forEach(function(t){(!e.getFieldInstance||e.getFieldInstance(t))&&(o[t]=f.current[t])}),e.setFieldsValue(o)}},rr=function(){var o=E();f.current=s(s({},f.current),o),T(function(t){return t==="simple"?"advance":"simple"})},Y=function(o){x&&setTimeout(function(){G().then(function(t){t===void 0&&(t={});var d=o||s(s({pageSize:a.defaultPageSize||10},(b==null?void 0:b[0])||{}),{current:1});if(!e){S(d);return}f.current=s(s({},f.current),t),S(d,t,{allFormData:f.current,type:C})}).catch(function(t){return t})})},ar=function(){var o,t;e&&e.resetFields(),Y(s(s({},(n==null?void 0:n[0])||{}),{pageSize:a.defaultPageSize||((t=(o=a.defaultParams)===null||o===void 0?void 0:o[0])===null||t===void 0?void 0:t.pageSize)||10,current:1}))},er=function(o){var t,d,k;(t=o==null?void 0:o.preventDefault)===null||t===void 0||t.call(o),Y(A.current?void 0:s({pageSize:a.defaultPageSize||((k=(d=a.defaultParams)===null||d===void 0?void 0:d[0])===null||k===void 0?void 0:k.pageSize)||10,current:1},(n==null?void 0:n[0])||{}))},tr=function(o,t,d,k){var V=h(b||[]),H=V[0],nr=V.slice(1);S.apply(void 0,M([s(s({},H),{current:o.current,pageSize:o.pageSize,filters:t,sorter:d,extra:k})],h(nr),!1))};P.useEffect(function(){if(b.length>0){f.current=(j==null?void 0:j.allFormData)||{},O(),S.apply(void 0,M([],h(b),!1));return}x&&(f.current=(n==null?void 0:n[1])||{},O(),u||Y(n==null?void 0:n[0]))},[]),K(function(){x&&O()},[C]);var B=P.useRef(!1);return B.current=!1,K(function(){!u&&x&&(B.current=!0,e&&e.resetFields(),f.current=(n==null?void 0:n[1])||{},O(),Y(n==null?void 0:n[0]))},[x]),K(function(){B.current||x&&(u||(B.current=!0,a.refreshDepsAction?a.refreshDepsAction():c.pagination.changeCurrent(1)))},M([],h(I),!1)),s(s({},c),{tableProps:{dataSource:((l=c.data)===null||l===void 0?void 0:l.list)||U.current,loading:c.loading,onChange:z(tr),pagination:{current:c.pagination.current,pageSize:c.pagination.pageSize,total:c.pagination.total}},search:{submit:z(er),type:C,changeType:z(rr),reset:z(ar)}})};async function vr(i,a){return{list:(await W.request({url:"/user/list",method:"get",params:{...i,...a}})).data.data,total:0}}function $(i){return W.request({url:"/user/",method:i.id?"put":"post",data:i})}function hr(){const[i]=m.useForm(),{userInfo:a}=X(n=>n.auth),{getInfo:l}=or().auth,{run:e,loading:p}=Q($,{manual:!0,onSuccess:()=>{l(),L.success("保存成功")}});P.useEffect(()=>{a&&i.setFieldsValue(a)},[a]);function w(n){if(n.password&&n.password!==n.confirmPassword)return L.error("两次输入密码不一致");e({...n,id:a.id})}return r.jsxs(r.Fragment,{children:[r.jsx("style",{children:`
                .user-info-card .ant-card {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }

                .user-info-card .ant-card-head {
                    background: #222226;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-info-card .ant-card-head-title {
                    color: #f0f0f2;
                    font-weight: 600;
                }

                .user-info-card .ant-form-item-label > label {
                    color: #f0f0f2;
                    font-weight: 500;
                }

                .user-info-card .ant-input,
                .user-info-card .ant-input-password {
                    background: #141416;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #f0f0f2;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-input:hover,
                .user-info-card .ant-input-password:hover {
                    border-color: rgba(212, 168, 82, 0.4);
                }

                .user-info-card .ant-input:focus,
                .user-info-card .ant-input-password:focus,
                .user-info-card .ant-input-focused {
                    border-color: #d4a852;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.15);
                }

                .user-info-card .ant-input::placeholder {
                    color: #6a6a72;
                }

                .user-info-card .ant-input-password .ant-input {
                    background: transparent;
                    border: none;
                }

                .user-info-card .ant-input-suffix {
                    color: #a0a0a8;
                }

                .user-info-card .ant-btn-primary {
                    background: #d4a852;
                    border-color: #d4a852;
                    color: #0d0d0f;
                    font-weight: 600;
                    height: 40px;
                    padding: 0 32px;
                    box-shadow: 0 2px 8px rgba(212, 168, 82, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-btn-primary:hover {
                    background: #e8c780 !important;
                    border-color: #e8c780 !important;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4) !important;
                    transform: translateY(-2px);
                }

                .user-info-card .ant-btn-primary:active {
                    transform: translateY(0);
                }

                .user-info-card .ant-form-item-explain-error {
                    color: #ff4d4f;
                }
            `}),r.jsx(Z,{title:"用户信息",className:"user-info-card",style:{background:"#1a1a1d",border:"1px solid rgba(255, 255, 255, 0.08)",boxShadow:"0 2px 8px rgba(0, 0, 0, 0.3)"},styles:{header:{background:"#222226",borderBottom:"1px solid rgba(255, 255, 255, 0.08)",color:"#f0f0f2"}},children:r.jsxs(m,{form:i,layout:"vertical",onFinish:w,children:[r.jsxs(sr,{gutter:20,children:[r.jsx(N,{span:24,lg:12,children:r.jsx(m.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:r.jsx(F,{})})}),r.jsxs(N,{span:24,lg:12,children:[r.jsx(m.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:r.jsx(F,{})})," "]}),r.jsxs(N,{span:24,lg:12,children:[r.jsx(m.Item,{name:"password",label:"新密码",children:r.jsx(F.Password,{})})," "]}),r.jsx(N,{span:24,lg:12,children:r.jsx(m.Item,{name:"confirmPassword",label:"确认新密码",children:r.jsx(F.Password,{})})})]}),r.jsx(ir,{type:"primary",htmlType:"submit",loading:p,children:"保存"})]})})]})}function wr(i){const{form:a,initValues:l,...e}=i,p=l==null?void 0:l.id;return r.jsxs(r.Fragment,{children:[r.jsx("style",{children:`
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
            `}),r.jsx(dr,{title:p?"编辑用户":"新建用户",...e,className:"user-modal",children:r.jsxs(m,{layout:"vertical",form:a,children:[r.jsx(m.Item,{name:"name",label:"名称",rules:[{required:!0,message:"请输入名称"}],children:r.jsx(F,{})}),r.jsx(m.Item,{name:"username",label:"用户名",rules:[{required:!0,message:"请输入用户名"}],children:r.jsx(F,{})}),r.jsx(m.Item,{name:"password",label:"新密码",rules:[{required:!p}],children:r.jsx(F.Password,{})}),r.jsx(m.Item,{name:"confirmPassword",label:"确认新密码",rules:[{required:!p}],children:r.jsx(F.Password,{})})]})})]})}function yr(){const{message:i}=lr.useApp(),{tableProps:a,refresh:l}=xr(vr),{setOpen:e,modalProps:p,form:w}=ur({service:$,onOk:()=>{i.success("保存成功"),e(!1),l()}}),n=[{title:"名称",dataIndex:"name"},{title:"用户名",dataIndex:"username"},{title:"管理员",dataIndex:"is_admin",render:u=>u?"是":"否"},{title:"",dataIndex:"operations",width:20,render:(u,g)=>!g.is_admin&&r.jsx(br,{onClick:I=>_(I,g)})}];function _(u,g){u==="edit"&&e(!0,g)}return r.jsxs(r.Fragment,{children:[r.jsx("style",{children:`
                .user-list-card .ant-card {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }

                .user-list-card .ant-card-head {
                    background: #222226;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-list-card .ant-card-head-title {
                    color: #f0f0f2;
                    font-weight: 600;
                }

                .user-list-card .ant-card-extra {
                    padding: 0;
                }

                .user-list-card .ant-table {
                    background: transparent;
                }

                .user-list-card .ant-table-thead > tr > th {
                    background: #222226;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                    color: #f0f0f2;
                    font-weight: 600;
                    padding: 16px;
                }

                .user-list-card .ant-table-tbody > tr {
                    background: transparent;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-list-card .ant-table-tbody > tr > td {
                    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                    color: #a0a0a8;
                    padding: 16px;
                }

                .user-list-card .ant-table-tbody > tr:hover {
                    background: rgba(212, 168, 82, 0.08) !important;
                }

                .user-list-card .ant-table-tbody > tr:hover > td {
                    color: #f0f0f2;
                    border-bottom-color: rgba(212, 168, 82, 0.15);
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
                    background: #d4a852;
                    color: #0d0d0f;
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 2px 6px rgba(212, 168, 82, 0.3);
                }

                .user-list-card .icon-button:hover {
                    background: #e8c780;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4);
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
                    color: #6a6a72;
                }
            `}),r.jsxs(Z,{title:"用户管理",extra:r.jsx(mr,{onClick:()=>e(!0),children:r.jsx(fr,{})}),className:"user-list-card",style:{background:"#1a1a1d",border:"1px solid rgba(255, 255, 255, 0.08)",boxShadow:"0 2px 8px rgba(0, 0, 0, 0.3)"},styles:{header:{background:"#222226",borderBottom:"1px solid rgba(255, 255, 255, 0.08)",color:"#f0f0f2"},body:{padding:0}},children:[r.jsx(cr,{rowKey:"id",columns:n,...a,pagination:!1}),r.jsx(wr,{form:w,...p})]})]})}function Sr(){const{userInfo:i}=X(a=>a.auth);return r.jsxs(pr,{direction:"vertical",style:{width:"100%"},children:[r.jsx(hr,{}),(i==null?void 0:i.is_admin)&&r.jsx(yr,{})]})}export{Sr as component};
