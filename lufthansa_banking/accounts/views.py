from rest_framework.views import APIView
from rest_framework.response import Response
from utils import logger
from .models import Account, AccountRequest, Card, CardRequest
from .serializers import AccountSerializer, AccountRequestSerializer, CardSerializer, CardRequestSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError


class AccountViewSet(ModelViewSet):
    """Viewset for Account model"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def create(self, request):
        """Account POST method"""
        if self.request.user.type == "CUSTOMER":
            return Response({"error": "Only bankers or admins can create accounts."}, status=403)

        serializer = AccountSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            if request.user.type == 'CUSTOMER':
                return Response({"error": "Customer can't create accounts"}, 403)
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').info(f"Account creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, PUT, DELETE methods for Account"""
        try:
            if self.request.user.type == 'CUSTOMER' and self.request.method == "DELETE":
                return Response({"error": "Customer can't delete accounts"}, 201)
            if self.request.user.type == 'CUSTOMER':
                user = self.request.user
                accounts = Account.objects.filter(user=user)
            else:
                accounts = Account.objects.all()
            if accounts.exists():
                return accounts
            raise Account.DoesNotExist
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Card.objects.none()
        
class CardViewSet(ModelViewSet):
    """Viewset for Card model"""
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def perform_create(self, serializer):
        """Card POST method"""
        if self.request.user.type == 'CUSTOMER':
            return Response({"error": "Customer can't create cards"}, 403)

        try:
            if self.request.user.type == "CUSTOMER":
                return Response({"error": "Only bankers or admins can create accounts."}, status=403)
        
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').info(f"Card creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, DELETE methods for Card"""
        try:
            if self.request.user.type == 'CUSTOMER' and self.request.method == "DELETE":
                return Response({"error": "Customer can't delete cards"}, 403)

            if self.request.user.type == 'CUSTOMER':
                user = self.request.user
                accounts = Account.objects.filter(user=user)  
                cards = Card.objects.filter(account__in=accounts)  
            else:
                cards = Card.objects.all()

            return cards if cards.exists() else Card.DoesNotExist
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Card.objects.none()

class AccountRequestViewSet(ModelViewSet):
    """Viewset for AccountRequest model"""
    queryset = AccountRequest.objects.all()
    serializer_class = AccountRequestSerializer

    def perform_create(self, serializer):
        """AccountRequest POST method"""
        try:
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').info(f"Account request creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, DELETE methods for AccountRequest"""
        try:
            if self.request.user.type == 'CUSTOMER' and self.request.method == "DELETE":
                return Response({"error": "Customer can't delete account requests"}, 201)

            if self.request.user.type == 'CUSTOMER':
                account_request = AccountRequest.objects.filter(user=self.request.user)
            account_request = AccountRequest.objects.all()
            if account_request.exists():
                return account_request
            raise AccountRequest.DoesNotExist
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return AccountRequest.objects.none()

class CardRequestViewSet(ModelViewSet):
    """Viewset for CardRequest model"""
    queryset = CardRequest.objects.all()
    serializer_class = CardRequestSerializer

    def perform_create(self, serializer):
        """CardRequest POST method"""

        try:
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            print(e)
            logger('ACCOUNTS').info(f"Card request creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, DELETE methods for CardRequest"""

        try:
            if self.request.user.type == 'CUSTOMER' and self.request.method == "DELETE":
                return Response({"error": "Customer can't delete card requests"}, 201)

            if self.request.user.type == 'CUSTOMER' and self.request.method == "DELETE":
                return Response({"error": "Customer can't delete card requests"}, 201)

            if self.request.user.type == 'CUSTOMER':
                user = self.request.user
                accounts = Account.objects.filter(user=user)  
                cards = Card.objects.filter(account__in=accounts)  
            card_request = CardRequest.objects.all()
            if card_request.exists():
                return card_request
            raise CardRequest.DoesNotExist
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return CardRequest.objects.none()
        

class ApproveAccountRequestView(APIView):
    """Approve account request"""
    def post(self, request, id):
        """POST method for approving account request"""

        if request.user.type == 'CUSTOMER':
            return Response({"error": "Customer can't approve account"}, 403)
        try:
            account_request = AccountRequest.objects.get(pk=id, status='PENDING')
            account_request.approve() 
            return Response({"message": "Account request approved."}, status=200)
        except AccountRequest.DoesNotExist:
            return Response({"error": "Account request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
class RejectAccountRequestView(APIView):
    """Reject account request"""

    def post(self, request, id):
        """POST method for rejecting account request"""
        if request.user.type == 'CUSTOMER':
            return Response({"error": "Customer can't reject accounts"}, 403)
        try:
            account_request = AccountRequest.objects.get(pk=id, status='PENDING')
            account_request.reject(request.data.get('description', ''))
            return Response({"message": "Account request rejected."}, status=200)
        except AccountRequest.DoesNotExist:
            return Response({"error": "Account request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

class ApproveCardRequestView(APIView):
    """Approve card request"""

    def post(self, request, id):
        """POST method for approving card request"""
        if request.user.type == 'CUSTOMER':
            return Response({"error": "Customer can't approve cards"}, 403)
        try:
            card_request = CardRequest.objects.get(pk=id, status='PENDING')
            card_request.approve() 
            return Response({"message": "Card request approved."}, status=200)
        except CardRequest.DoesNotExist:
            return Response({"error": "Card request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
    
class RejectCardRequestView(APIView):
    """Reject card request"""

    def post(self, request, id):
        """POST method for rejecting card request"""
        if request.user.type == 'CUSTOMER':
            return Response({"error": "Customer can't reject cards"}, 403)
        try:

            card_request = CardRequest.objects.get(pk=id, status='PENDING')
            card_request.reject(request.data.get('description', ''))
            return Response({"message": "Card request rejected."}, status=200)
        except CardRequest.DoesNotExist:
            return Response({"error": "Card request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)