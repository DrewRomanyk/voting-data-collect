Vote
- PK: congress, chamber, session, roll_call
- bill_slug
- question

MemberVote
- PK: Member(PK) & Vote(PK)
- vote_position

Bill
- PK: bill_slug & congress
- title
- short_title
- summary
- summary_short

Member
- PK: member_id
- name
- date_of_birth
- url
- current_party

Category
- PK: id
- name

Issue
- PK: id
- name

BillIssue
- PK: Bill(PK) & Issue(PK)
- stance

MemberIssue
- PK: Member(PK) & Issue(PK)
- stance