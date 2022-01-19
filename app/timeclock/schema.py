import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q
from datetime import date, datetime, timedelta
from django.utils import timezone
import calendar

from .models import Clock

class ClockType(DjangoObjectType):
    class Meta:
        model = Clock


class CurrentClock(graphene.ObjectType):
    clock = graphene.Field(ClockType)

    def resolve_clock(parent, info):
        return parent

class ClockedHours(graphene.ObjectType):
    today = graphene.Int()
    currentWeek = graphene.Int()
    currentMonth = graphene.Int()

class Query(graphene.ObjectType):
    current_clock = graphene.Field(CurrentClock)
    clocked_hours = graphene.Field(ClockedHours)

    def resolve_current_clock(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("User must login first")
        filter = (
            Q(user=user) &
            Q(clockedOut=None)
        )
        clock = Clock.objects.filter(filter).first()
        return clock

    def resolve_clocked_hours(self, info):
        today = 0
        currentWeek = 0
        currentMonth = 0
        dt = datetime.now()
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("User must login first")
        filter = (
            Q(user=user) 
        )
        clock = Clock.objects.filter(filter)
        for c in clock:
            # today
            if c.clockedIn.date() == datetime.now().date():
                if c.clockedOut:
                    tot_diff = c.clockedOut - c.clockedIn
                else:
                    tot_diff = datetime.now(timezone.utc) - c.clockedIn
                today = today + (tot_diff.days * 24 + tot_diff.seconds / 3600.0)
                today = today + (tot_diff.total_seconds() / 3600)
            # currentWeek
            if  c.clockedIn.date() in get_current_week(datetime.now().date()):
                if c.clockedOut:
                    tot_diff = c.clockedOut - c.clockedIn
                else:
                    tot_diff = datetime.now(timezone.utc) - c.clockedIn
                currentWeek = currentWeek + (tot_diff.days * 24 + tot_diff.seconds / 3600.0)
                currentWeek = currentWeek + (tot_diff.total_seconds() / 3600)
            # currentMonth
            if  c.clockedIn.date().month == datetime.now().month:
                if c.clockedOut:
                    tot_diff = c.clockedOut - c.clockedIn
                else:
                    tot_diff = datetime.now(timezone.utc) - c.clockedIn
                currentMonth = currentMonth + (tot_diff.days * 24 + tot_diff.seconds / 3600.0)
                currentMonth = currentMonth + (tot_diff.total_seconds() / 3600)

        return {"today": today, "currentWeek":currentWeek,"currentMonth":currentMonth}

one_day = timedelta(days=1)

def get_current_week(date):
  day_idx = (date.weekday() + 1) % 7  
  sunday = date - timedelta(days=day_idx)
  date = sunday
  for n in range(7):
    yield date
    date += one_day

class ClockIn(graphene.Mutation):
    clock = graphene.Field(ClockType)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("user must logged in to update clock.")
        clock = Clock(user=user, clockedIn=timezone.now())
        clock.save()
        return ClockIn(clock=clock)

class ClockOut(graphene.Mutation):
    clock = graphene.Field(ClockType)
    
    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("user must logged in to update clock.")

        filter = (
            Q(user=user) &
            Q(clockedOut=None)
        )
        clock = Clock.objects.filter(filter).first()
        if clock:
            clock = Clock.objects.get(id=clock.id)
            clock.clockedOut = timezone.now()
            clock.save()

        return ClockOut(clock=clock)


class Mutation(graphene.ObjectType):
    clock_in = ClockIn.Field()
    clock_out = ClockOut.Field()
