class Vote:
    def __init__(self, congress, chamber, session, roll_call, bill_slug, question):
        # PK
        self.congress = congress
        self.chamber = chamber
        self.session = session
        self.roll_call = roll_call
        # Other
        self.bill_slug = bill_slug
        self.question = question
    
    @staticmethod
    def from_api_data(vote_data):
        vote = Vote(
            vote_data['congress'],
            vote_data['chamber'],
            vote_data['session'],
            vote_data['roll_call'],
            vote_data['bill']['bill_id'].split('-')[0],
            vote_data['question'],
        )
        return vote

class MemberVote:
    def __init__(self, member_id, congress, chamber, session, roll_call, vote_position):
        # PK
        self.member_id = member_id
        self.congress = congress
        self.chamber = chamber
        self.session = session
        self.roll_call = roll_call
        # Other
        self.vote_position = vote_position
    
    @staticmethod
    def from_api_data(member_vote_data, vote):
        member_vote = MemberVote(
            member_vote_data['member_id'],
            vote.congress,
            vote.chamber,
            vote.session,
            vote.roll_call,
            member_vote_data['vote_position'],
        )
        return member_vote

class Bill:
    def __init__(self, bill_slug, congress, title, short_title, summary, summary_short):
        # PK
        self.bill_slug = bill_slug
        self.congress = congress
        # Other
        self.title = title
        self.short_title = short_title
        self.summary = summary
        self.summary_short = summary_short
    
    @staticmethod
    def from_api_data(bill_data):
        bill = Bill(
            bill_data['bill_slug'],
            bill_data['congress'],
            bill_data['title'],
            bill_data['short_title'],
            bill_data['summary'],
            bill_data['summary_short'],
        )
        return bill

class Member:
    def __init__(self, member_id, name, date_of_birth, url, current_party):
        # PK
        self.member_id = member_id
        # Other
        self.name = name
        self.date_of_birth = date_of_birth
        self.url = url
        self.current_party = current_party
    
    @staticmethod
    def from_api_data(member_data):
        member = Member(
            member_data['member_id'],
            member_data['first_name'] + " " + member_data['last_name'],
            member_data['date_of_birth'],
            member_data['url'],
            member_data['current_party']
        )
        return member


