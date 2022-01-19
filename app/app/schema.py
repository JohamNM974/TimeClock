import graphene
import users.schema
import timeclock.schema
import graphql_jwt

class Query(users.schema.Query, timeclock.schema.Query, graphene.ObjectType):
    pass

class Mutation(users.schema.Mutation, timeclock.schema.Mutation, graphene.ObjectType):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)