# Business rules

## Tokens

- ReplyFlow does not assume fixed people or fields for an interaction.
- A token is a reusable marker written as `<name>` inside a response structure.
- Token names accept lowercase letters, numbers and underscores; input is normalized before storage.
- Administrators create global tokens. Standard users create tokens visible only to their own account.
- Token values are not stored with the token definition. They must be supplied in the **Informacoes dos tokens** field when generating a reply.
- The AI may use the received message as additional context, but must not invent missing token values.
- When a required token has no supplied value, its marker is preserved for manual review.
