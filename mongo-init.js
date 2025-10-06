db = db.getSiblingDB('chat-db'); // later to env

db.messages.createIndexes([
  { key: { conversationId: 1, createdAt: -1 } },
  { key: { conversationId: 1, _id: -1 } },
  { key: { authorId: 1, createdAt: -1 } },
  { key: { "content.text": "text" } }
]);

db.conversations.createIndexes([
  { key: { "participants.userId": 1, updatedAt: -1 } },
  { key: { updatedAt: -1 } }
]);
