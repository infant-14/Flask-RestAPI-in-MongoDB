from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/booksdb"
mongo = PyMongo(app)


# Endpoint to get books from the specified page with pagination
#@app.route('/books', methods=['GET'])
#def get_books():
    #page = int(request.args.get('page', 1))
    #per_page = 10
    #books = mongo.db.books.find().skip((page - 1) * per_page).limit(per_page)
    #return jsonify({'books': [book for book in books]})

@app.route('/books', methods=['GET'])
def get_books():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    books = mongo.db.books.find().skip((page - 1) * per_page).limit(per_page)
    total_items = mongo.db.books.count_documents({})
    total_pages = (total_items + per_page - 1) // per_page
    books_list = [{'id': str(book['_id']), 'title': book['title'], 'author': book['author'], 'category_id': str(book['category_id'])} for book in books]
    response = {
        'books': books_list,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_items
    }
    return jsonify(response), 200

@app.route('/filtered-books', methods=['GET'])
def filter_books():
    author = request.args.get('author')
    category_id = request.args.get('category_id')
    sort_by_title = request.args.get('sort_by_title')
    
    query = {}
    if author:
        query['author'] = author
    if category_id:
        query['category_id'] = category_id
    
    books = mongo.db.books.find(query)
    if sort_by_title:
        sort_order = 1 if request.args.get('sort_order') == '1' else -1
        books = books.sort('title', sort_order)
    
    # Convert ObjectId to string for JSON serialization
    filtered_books = [{'_id': str(book['_id']), 'title': book['title'], 'author': book['author']} for book in books]
    
    return jsonify({'filtered_books': filtered_books})

@app.route('/books/<book_id>', methods=['GET'])
def get_book_by_id(book_id):
     book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
     if book:
        return jsonify({'book': {'_id': str(book['_id']), 'title': book['title'], 'author': book['author']}})
     else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/books/author/<author_name>', methods=['GET'])
def get_books_by_author(author_name):
    books = mongo.db.books.find({'author': author_name})
    if books:
        books_data = [{'_id': str(book['_id']), 'title': book['title'], 'author': book['author']} for book in books]
        return jsonify({'books': books_data})
    else:
        return jsonify({'message': 'No books found for the author'}), 404


@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    new_book = {
        'id': data['id'],
        'title': data['title'],
        'author': data['author'],
        'category_id': data['category_id']
    }
    mongo.db.books.insert_one(new_book)
    return jsonify({'message': 'Book created successfully'})

@app.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category_id = mongo.db.categories.insert(data)
    return jsonify({'message': 'Category created successfully', 'id': str(category_id)})

# Endpoint to update a book
@app.route('/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    result = mongo.db.books.update_one({'_id': ObjectId(book_id)}, {'$set': data})
    if result.modified_count == 1:
        return jsonify({'message': 'Book updated successfully'}), 200
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    mongo.db.books.delete_one({'_id': ObjectId(book_id)})
    return jsonify({'message': 'Book deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)