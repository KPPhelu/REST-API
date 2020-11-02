from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()  # Initizlize parser
    parser.add_argument('price',  ## add argument to the parser, which it is going to look while parsing request
                        type=float,
                        required=True,
                        help='This field can not be left blank'
                        )
    parser.add_argument('store_id',  ## add argument to the parser, which it is going to look while parsing request
                        type=int,
                        required=True,
                        help='Every item needs a store id.'
                        )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not Found"}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'An item with name "{}" already exists'.format(name)}, 400

        data = Item.parser.parse_args()  ## parse arguments that come through JSON payload and put valid ones in data.
        # data = request.get_json(silent=True)
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occured inserting the item."}, 500 # code 500 is internal server error.

        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted'}
        return {'message': 'Item not found to delete in database'}


    def put(self, name):
        data = Item.parser.parse_args()  ## parse arguments that come through JSON payload and put valid ones in data.

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.query.all()]}
        ## Or equivalently by using lambda function as below
        # return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}