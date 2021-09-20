<h1>Import Order System For Employees</h1>
<hr/>
<b>Description</b>
<br/>
<p>
    System has 5 kinds of users with different roles assigned to them:<br/>
    <ul>
        <li>Client - can add new order and follow changes (including creating comments)</li>
        <li>Executor - is up to executing order (change statuses, stages etc.)</li>
        <li>Planner - set payment dates if is necessery</li>
        <li>Management - accept order if is necessery</li>
        <li>Admin (superuser) - all permissions, create new users</li>
    </ul>
    <br/>
    Order model includes 2 important fields - status and stage.<br/>
    Order has also own logs (model Log) which include additional informations.<br/>
    New log is creating when order data was changed (for example changed status)<br/>
    For stage changes is necessery to note deadline of executing this stage.<br/>
    <br/>
    <h3>API endpoints:</h3>
    <br/>
    <ul>
        <li>
            - <b>GET /admin/</b> - default Django admin system
        </li>
        <li>
            - <b>POST /api/auth/login/</b> - django-rest-auth login endpoint (required: username and password)
        </li>
        <li>
            - <b>POST /api/auth/logout/</b> - django-rest-auth logout system (required: token)
        </li>
        <li>
            - <b>GET /api/auth/user/</b> - get user data (required: token)
        </li>
        <li>
            - <b>GET /api/statuses/</b> - get statuses list
        </li>
        <li>
            - <b>GET /api/origins/</b> - get origins list
        </li>
        <li>
            - <b>GET /api/stages/</b> - get stages list
        </li>
        <li>
            - <b>GET /api/priorities/</b> - get priorities list
        </li>
        <li>
            - <b>CRUD /api/orders/</b> - CRUD for orders<br/>
            (
                - for updating accept only PATCH method,<br/>
                - not editable fields: title, content, owner and executor (unless admin is editing),<br/>
                - when status = NEW, PROCESSING - executor can edit,<br/>
                - when status = PAYMENT_AWAIT - planner can edit,<br/>
                - when status = APPROVAL_AWAIT - manager can edit,<br/>
                - admin always can edit
            )
        </li>
        <li>
            - <b>CRUD /api/order/{pk}/comments/</b> - CRUD for comments
        </li>
    </ul>
</p>

<hr/>

<h3>Used packages</h3>
<ul>
    <li>drf</li>
    <li>django-rest-auth</li>
    <li>drf-extensions</li>
</ul>
