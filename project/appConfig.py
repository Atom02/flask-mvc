DBPRODUCTION ={
	"host":'host',
	"port":3306,
	"user":'user',
	"password":'password',
	"db":'db'
}

DB = DBPRODUCTION

components = {
	"RBAC":{
		"itemTable": "auth_item",
        "itemChildTable": "auth_item_child",
        "assignmentTable": "auth_assignment",
        "ruleTable": "auth_rule",
        "groupTable": "auth_group"
	}
}