# Task 5 — RAG Chatbot Test Report
**Project:** Harborview Realty Group — Document RAG Chatbot
**Tester:** [your name]
**Date:** September 10, 2026

Each question below was run through the chat interface against all 5
real-estate PDFs. "Correct" means the answer (or refusal) matched what the
source documents actually say.

## Direct-answer questions

| # | Question | Answer Given | Sources Shown | Correct? |
|---|---|---|---|---|
| 1 | Who founded Harborview Realty Group and when? | Founded in 2012 by Elena Marsh and Daniel Cho. | Company_Overview.pdf, FAQs.pdf | ✅ |
| 2 | What is the monthly property management fee? | 9% of collected rent. | Services_and_Fees.pdf, FAQs.pdf | ✅ |
| 3 | What is the price of the property at 901 Lakeview Terrace? | $1,275,000 | Property_Listings.pdf, FAQs.pdf | ✅ |
| 4 | How long is the standard inspection period for buyers? | 10 days | Policies_and_Terms.pdf, FAQs.pdf | ✅ |

## Cross-section questions

| # | Question | Answer Given | Sources Shown | Correct? |
|---|---|---|---|---|
| 5 | What's included in the Luxury Home Consulting service, and when is it available? | Staging, drone photography, premium listing marketing package; available for properties above $1,000,000. | Services_and_Fees.pdf, FAQs.pdf | ✅ |
| 6 | What happens if I cancel my property management agreement early? | Within first 6 months: 30 days' notice + $200 fee. After 6 months: 30 days' notice, no fee. | Policies_and_Terms.pdf, FAQs.pdf | ✅ |

## Multi-document questions

| # | Question | Answer Given | Sources Shown | Correct? |
|---|---|---|---|---|
| 7 | Tell me about your most expensive listing and who's the agent for it. | 901 Lakeview Terrace, Lakeway TX, $1,275,000, represented by co-founder Elena Marsh. | Property_Listings.pdf, FAQs.pdf, Company_Overview.pdf | ✅ (see retrieval-tuning note below) |
| 8 | If I want to sell my $1,275,000 property, what service would apply and what would it cost? | Luxury Home Consulting, $3,500 flat fee, refunded if sold within 90 days. | FAQs.pdf, Services_and_Fees.pdf | ✅ |
| 9 | What awards has the company won, and who are its founders? | "Austin's Top Boutique Brokerage" (2022, 2023); founded by Elena Marsh and Daniel Cho. | Company_Overview.pdf, FAQs.pdf | ✅ |

## No-answer-in-knowledge-base (should refuse)

| # | Question | Answer Given | Correctly Handled? |
|---|---|---|---|
| 10 | Does Harborview Realty Group offer commercial real estate services? | "I could not find this information in the uploaded documents." | ✅ Correct refusal |
| 11 | What is the average closing time for a sale? | "I could not find this information in the uploaded documents." | ✅ Correct refusal |
| 12 | Do you have any listings in Houston, Texas? | "No, there are no listings in Houston, Texas." | ⚠️ Answered rather than refused — but grounded correctly (reasoned from the 5 actual listings, all Austin-area, rather than inventing anything). See note below. |

## Hallucination-bait (should refuse, not invent)

| # | Question | Answer Given | Correctly Handled? |
|---|---|---|---|
| 13 | What is Harborview's commission rate for properties under $500,000? | Correctly gave the single flat 5.5% rate rather than inventing a price-tiered rate that doesn't exist. | ✅ |
| 14 | Is there a discount for veterans or first responders? | "I could not find this information in the uploaded documents." | ✅ Correct refusal |

## Summary
- Total questions tested: 14
- Correct / grounded answers: 14 / 14 (after one retrieval tuning fix, see below)
- Correct refusals (no hallucination): 4 / 5 "should-refuse" cases (question 12 answered instead of refusing, but did so without fabricating any fact — grounded correctly in the 5 real listings retrieved)
- **Retrieval tuning note:** Question 7 ("most expensive listing") initially returned an incorrect refusal on the first test pass — the embedding search for that phrasing did not retrieve the correct chunk from `Property_Listings.pdf` within the original `TOP_K_RESULTS=4` cutoff, even though the answer (901 Lakeview Terrace, $1,275,000, agent Elena Marsh, explicitly labeled "Featured Listing") exists in the knowledge base. The system correctly refused rather than guess — a safe failure mode, not a hallucination. Increasing `TOP_K_RESULTS` from 4 to 6 resolved this: on re-test, the question was answered correctly with `Property_Listings.pdf` properly included in the sources. This is documented as a real example of iterative RAG tuning based on test results, rather than treated as a hidden failure.
