<template>
  <tr
    :key="competition.id"
    :id="competition.id"
    :class="{
      'has-text-grey-lighter': isPast(competition),
      'has-text-grey-light': competition.date.is_draft,
      'has-text-weight-light': competition.date.is_draft,
      'has-text-grey-lighter': competition.date.is_canceled,
      'is-selected': isCurrent(competition),
      'is-canceled': competition.date.is_canceled,
    }"
  >
    <td class="date">
      <div style="white-space: nowrap">
        {{ formatDate(competition.date.start) }}
      </div>

      <div
        v-if="
          formatDate(competition.date.start) != formatDate(competition.date.end)
        "
        style="white-space: nowrap"
      >
        - {{ formatDate(competition.date.end) }}
      </div>

      <p>
        <span
          :class="{
            tag: true,
            'is-success':
              formatDate(competition.date.registration_opens) !=
              formatDate(new Date()),
            'is-dark':
              formatDate(competition.date.registration_opens) ==
              formatDate(new Date()),
          }"
          v-if="competition.has_registration_pending"
          style="cursor: help"
          :title="
            'Anmeldung startet am ' +
            formatDate(competition.date.registration_opens)
          "
        >
          ⏰ {{ formatDate(competition.date.registration_opens) }}
        </span>
      </p>
    </td>
    <td>
      <div>
        <a v-if="competition.url" class="is-block" :href="competition.url">{{
          competition.name
        }}</a>
        <div v-else>{{ competition.name }}</div>
      </div>
      <div class="tags">
        <CompetitionTypeTag :competition="competition" />
        <LocationTag :competition="competition" />
        <span
          v-if="competition.date.is_canceled"
          class="tag"
          style="cursor: help"
          title="Diese Veranstaltung wurde abgesagt"
          >❌
        </span>
        <span
          v-if="competition.date.is_draft"
          class="tag"
          style="cursor: help"
          title="Der Termin dieser Veranstaltung ist noch nicht endgültig"
          >❓</span
        >
        <ParticipantCounter :competition="competition" />
        <SingleboerseCounter
          v-if="singleboerse[competition.id]"
          :id="singleboerse[competition.id]"
        />
      </div>
    </td>
  </tr>
</template>

<style scoped>
table th.date,
table td.date {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}

.is-canceled td {
  text-decoration: line-through;
}

tr:target {
  background-color: #00d1b2 !important;
  color: #fff;
}

@media screen and (max-width: 1024px) {
  table .date {
    width: 10%;
  }
}
@media screen and (min-width: 1024px) {
  table .date {
    width: 40%;
  }
}
</style>

<script setup>
import { differenceInDays, parseISO as parseIsoDate } from "date-fns";

defineProps(["competition"]);

const singleboerse = {
  recyC5LmxecehTxWD: "240511-schonach",
  reckHSB1eG9Su8fxx: "240907-radebeul",
};

const displayPastCompetitions = ref(false);
const competitionFilter = ref({
  FCC: true,
  FSR: true,
});

const formatDate = (date) =>
  new Date(date).toLocaleDateString("de-DE", {
    weekday: "short",
    month: "2-digit",
    day: "2-digit",
    year: "2-digit",
  });

const getDateFromDate = (date) => date.toISOString().substring(0, 10);

const isPast = (competition) =>
  getDateFromDate(new Date()) > getDateFromDate(new Date(competition.date.end));

const isCurrent = (competition) =>
  getDateFromDate(new Date()) >=
    getDateFromDate(new Date(competition.date.start)) &&
  getDateFromDate(new Date()) <=
    getDateFromDate(new Date(competition.date.end));
</script>
