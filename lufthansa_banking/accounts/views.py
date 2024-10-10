from rest_framework.views import APIView
from rest_framework.response import Response
from utils import logger
from .models import Account, Card
from .serializers import AccountSerializer, CardSerializer


# Create your views here.
class AccountListView(APIView):
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER':
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            accounts = Account.objects.all()
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            request.data['user_id'] = request.user.id
            serializer = AccountSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

class AccountView(APIView):
    
    def get(self, request, user_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER' and request.user.id != user_id:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            account = Account.objects.get(user_id=user_id)
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

    def put(self, request, user_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER':
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            account = Account.objects.get(user_id=user_id)
            serializer = AccountSerializer(account, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)        

    def delete(self, request, user_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER':
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            account = Account.objects.get(user_id=user_id)
            account.delete()
            return Response({"success": "Account deleted"}, status=204)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

class ApproveAccountRequestView(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            account_request = Account.objects.get(pk=pk, status='pending')
            account_request.approve()  # Call the approve method to change the status
            return Response({"message": "Account request approved."}, status=200)
        except Account.DoesNotExist:
            return Response({"error": "Account request not found or already processed."}, status=404)

class RejectAccountRequestView(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            account_request = Account.objects.get(pk=pk, status='pending')
            account_request.reject()  # Call the reject method to change the status
            return Response({"message": "Account request rejected."}, status=200)
        except Account.DoesNotExist:
            return Response({"error": "Account request not found or already processed."}, status=404)

class CardListView(APIView):
    def get(self, request, user_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER' and request.user.id != user_id:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            cards = Card.objects.filter(user_id=user_id)
            serializer = CardSerializer(cards, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

    def post(self, request, user_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER' and request.user.id != user_id:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            request.data['user_id'] = user_id
            serializer = CardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)      

class CardView(APIView):
    def get(self, request, user_id, card_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER' and request.user.id != user_id:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            card = Card.objects.get(card_id=card_id)
            serializer = CardSerializer(card)
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

    def put(self, request, card_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER':
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            card = Card.objects.get(card_id=card_id)
            serializer = CardSerializer(card, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

    def delete(self, request, card_id):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            if request.user.user_type == 'CUSTOMER':
                return Response({"error": "You do not have access to this resource"}, status=403)
            
            card = Card.objects.get(card_id=card_id)
            card.delete()
            return Response({"success": "Card deleted"}, status=204)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        