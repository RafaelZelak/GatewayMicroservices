// Substitua pelas suas credenciais diretamente
const adminUser = "admin_root";
const adminPass = "senha_root_123!";
const appUser = "app_user";
const appPass = "senh@Complexa_321!";
const dbName = "gateway_db";

// Conectar como admin
db = db.getSiblingDB('admin');
db.auth(adminUser, adminPass);

// Criar database da aplicação
const appDB = db.getSiblingDB(dbName);

// Criar usuário da aplicação
appDB.createUser({
  user: appUser,
  pwd: appPass,
  roles: [
    { role: "readWrite", db: dbName },
    { role: "dbAdmin", db: dbName }
  ]
});

// Criar coleção de metadados
appDB.createCollection("system_metadata");
appDB.system_metadata.insertOne({
  event: "initial_setup",
  createdAt: new Date(),
  version: "3.0.0"
});

print("✅ Configuração inicial do MongoDB concluída com sucesso!");
