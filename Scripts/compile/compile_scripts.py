from Utilities.compiler import compile_module


compile_module(
    root='../../Release/GoldenWhims',
    mod_scripts_folder='..',
    include_folders=('goldwhims_scripts',),
    mod_name='GoldenWhims'
)
