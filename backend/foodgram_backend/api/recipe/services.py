from pathlib import Path

from borb.pdf import (
    Document,
    PDF,
    Page,
    Paragraph,
    SingleColumnLayout,
)
import logging
import traceback

def create_file(recipes, username):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    try:
        pdf = Document()

        page = Page()
        pdf.add_page(page)

        layout = SingleColumnLayout(page)

        ingredients = {}

        for recipe in recipes.all():

            all_recipe_ingredients = recipe.ingredients.all()

            for ingredient in all_recipe_ingredients:
                if ingredients.get(ingredient.ingredient.name):
                    ingredients[ingredient.ingredient.name][1] += ingredient.weight
                else:
                    ingredients[ingredient.ingredient.name] = [
                        ingredient.ingredient.measurement_unit,
                        ingredient.weight
                    ]

        for key, value in ingredients.items():
            layout.add(
                Paragraph(f'{key} ({str(value[0])}) -- {str(value[1])}')
            )

        path_to_user_media = Path(
            f'{BASE_DIR}/media/recipe/users/shop_list/{username}/'
        )

        if not path_to_user_media.exists():
            path_to_user_media.mkdir(parents=True, exist_ok=True)

        with open(Path(f'{path_to_user_media}/output.pdf'), "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, pdf)
        return 'Created'
    except Exception as e:
        logging.error(traceback.format_exc())
