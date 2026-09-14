/**
 * Редактор блока «Форма „Предложить ресурс"».
 *
 * В панели можно посмотреть состояния формы, не отправляя её.
 */
( function ( blocks, element, components, blockEditor, ServerSideRender, i18n ) {
	'use strict';

	var el = element.createElement;
	var __ = i18n.__;

	blocks.registerBlockType( 'designstack/suggest-form', {
		edit: function ( props ) {
			var attributes = props.attributes;

			return el(
				element.Fragment,
				{},
				el(
					blockEditor.InspectorControls,
					{},
					el(
						components.PanelBody,
						{ title: __( 'Состояние для просмотра', 'designstack-core' ) },
						el( components.SelectControl, {
							label: __( 'Показать форму как', 'designstack-core' ),
							help: __( 'Влияет только на превью в редакторе, на сайте состояние приходит от отправки.', 'designstack-core' ),
							value: attributes.preview,
							options: [
								{ label: __( 'По умолчанию', 'designstack-core' ), value: 'default' },
								{ label: __( 'Ошибки полей', 'designstack-core' ), value: 'error' },
								{ label: __( 'Сбой отправки', 'designstack-core' ), value: 'failed' },
								{ label: __( 'Лимит отправок', 'designstack-core' ), value: 'limit' }
							],
							onChange: function ( value ) {
								props.setAttributes( { preview: value } );
							}
						} )
					)
				),
				el(
					'div',
					blockEditor.useBlockProps(),
					el( ServerSideRender, {
						block: 'designstack/suggest-form',
						attributes: attributes
					} )
				)
			);
		},
		save: function () {
			return null;
		}
	} );
} )(
	window.wp.blocks,
	window.wp.element,
	window.wp.components,
	window.wp.blockEditor,
	window.wp.serverSideRender,
	window.wp.i18n
);
