<?php
/**
 * Разметка блока «Подборка для старта».
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- разметка собрана с экранированием, kses вырезал бы svg иконок.
echo designstack_core_render_starter();
