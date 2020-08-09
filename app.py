# Imports
from flask import Flask, request
from flask_restx import Api, Resource, fields


# Initializations
# Initialize server
app = Flask(__name__)
# Initialize API
api = Api(
    app=app,
    version='1.0.0',
    title='Flask Swagger',
    description='Python web API Swagger UI boilerplate',
    validate=True
)
# Initialize namespace
ns = api.namespace(
    'products',
    description='Minimalistic product catalogue management API'
)


# Product model
product_model = api.model('Product', {
    'id': fields.Integer(
        required=True,
        description='Product id',
        help='Required field'
    ),
    'name': fields.String(
        required=True,
        description='Product name',
        help='Required field'
    ),
    'description': fields.String(
        required=True,
        description='Product description',
        help='Required field'
    ),
    'price': fields.Integer(
        required=True,
        description='Product price',
        help='Required field'
    ),
    'quantity': fields.Integer(
        required=True,
        description='Product quantity',
        help='Required field'
    )
})


# Product data access object
class ProductDAO:
    def __init__(self):
        self.idx = 0
        self.products = []

    def retrieve(self, id):
        for product in self.products:
            if product['id'] == id:
                return product

        raise FileNotFoundError(f'Product {id} Was Not Found')

    def create(self, data):
        product = data
        self.idx += 1
        product['id'] = self.idx
        self.products.append(product)

        return product

    def update(self, id, data):
        product = self.retrieve(id)
        product.update(data)

        return product

    def remove(self, id):
        product = self.retrieve(id)
        self.products.remove(product)


# Initialize data access object
dao = ProductDAO()
# Create mock products
for i in range(1, 4):
    dao.create({
        'name': f'Product {i}',
        'description': f'This is product {i}',
        'price': 10 ** (i - 1),
        'quantity': 10 ** i
    })


# Responses
products_get_responses = {
    200: 'OK',
    500: 'Internal Server Error'
}
products_post_responses = {
    201: 'Created',
    400: 'Bad Request',
    500: 'Internal Server Error'
}
product_get_responses = {
    200: 'OK',
    404: 'Not Found',
    500: 'Internal Server Error'
}
product_put_responses = {
    202: 'Accepted',
    400: 'Bad Request',
    404: 'Not Found',
    500: 'Internal Server Error'
}
product_delete_responses = {
    204: 'No Content',
    404: 'Not Found',
    500: 'Internal Server Error'
}


# Parameters
product_params = {'product_id': 'Unique Product ID'}


# Error handlers
def error_400_handler(namespace, error):
    namespace.abort(
        400,
        error.__doc__,
        status='Bad Request',
        statusCode='400'
    )


def error_404_handler(namespace, error):
    namespace.abort(
        404,
        error.__doc__,
        status='Not Found',
        statusCode='404'
    )


def error_500_handler(namespace, error):
    namespace.abort(
        500,
        error.__doc__,
        status='Internal Server Error',
        statusCode='500'
    )


# Routes
@ns.route('/')
class Products(Resource):
    @ns.doc(responses=products_get_responses)
    def get(self):
        try:
            return {
                'status': 'Existing Products Retrieved Successfully',
                'products': dao.products
            }, 200
        except Exception as error:
            error_500_handler(ns, error)

    @ns.doc(responses=products_post_responses)
    @ns.expect(product_model)
    def post(self):
        try:
            product = dao.create({
                'name': request.json['name'],
                'description': request.json['description'],
                'price': request.json['price'],
                'quantity': request.json['quantity']
            })

            return {
                'status': 'New Product Created Successfully',
                'product': product
            }, 201
        except UnboundLocalError as error:
            error_400_handler(ns, error)
        except Exception as error:
            error_500_handler(ns, error)


@ns.route('/<int:product_id>')
class Product(Resource):
    @ns.doc(responses=product_get_responses, params=product_params)
    def get(self, product_id):
        try:
            product = dao.retrieve(product_id)

            return {
                'status': 'Existing Product Retrieved Successfully',
                'product': product
            }, 200
        except FileNotFoundError as error:
            error_404_handler(ns, error)
        except Exception as error:
            error_500_handler(ns, error)

    @ns.doc(responses=product_put_responses, params=product_params)
    @ns.expect(product_model)
    def put(self, product_id):
        try:
            product = dao.update(product_id, {
                'name': request.json['name'],
                'description': request.json['description'],
                'price': request.json['price'],
                'quantity': request.json['quantity']
            })

            return {
                'status': 'Existing Product Updated Successfully',
                'product': product
            }, 202
        except UnboundLocalError as error:
            error_400_handler(ns, error)
        except FileNotFoundError as error:
            error_404_handler(ns, error)
        except Exception as error:
            error_500_handler(ns, error)

    @ns.doc(responses=product_delete_responses, params=product_params)
    def delete(self, product_id):
        try:
            dao.remove(product_id)

            return {'status': 'Existing Product Removed Successfully'}, 204
        except FileNotFoundError as error:
            error_404_handler(ns, error)
        except Exception as error:
            error_500_handler(ns, error)


# Run server
if __name__ == '__main__':
    app.run(debug=True)
