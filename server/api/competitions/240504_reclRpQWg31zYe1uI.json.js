import { defineEventHandler } from "h3";

export const teams = () => [];
export const participants = () => [];
export const count = () => 800;

export default defineEventHandler(async (event) => await count());
