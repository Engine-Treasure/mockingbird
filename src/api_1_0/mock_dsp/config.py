from flask_restful import fields

bdxmaterials_fields = {
    "type_id": fields.Integer,
    "name": fields.String,
    "path": fields.String
}

adowner_fields = {
    "oem_id": fields.Integer,
    # "bdx_id": fields.Integer,
    "name": fields.String,
    "area": fields.String,
    "category": fields.String,
    "brand": fields.String,
    "turn": fields.String,
    "url": fields.String,
    "lic": fields.String,
    "org": fields.String,
    "tax": fields.String,
    "reg": fields.String,
    "icp": fields.String,
    "card": fields.String,
    "bdx_materials": fields.List(fields.Nested(bdxmaterials_fields)),
    "adx": fields.List(fields.String),
    "adx_id": fields.List(fields.Integer)
}
