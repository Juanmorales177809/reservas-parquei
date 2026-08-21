// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'notificacion.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Notificacion {

 int get id; int get usuarioId; int? get reservaId; TipoNotificacion get tipo; bool get leida; String get createdAt; String get mensaje;
/// Create a copy of Notificacion
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NotificacionCopyWith<Notificacion> get copyWith => _$NotificacionCopyWithImpl<Notificacion>(this as Notificacion, _$identity);

  /// Serializes this Notificacion to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Notificacion&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.reservaId, reservaId) || other.reservaId == reservaId)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.leida, leida) || other.leida == leida)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.mensaje, mensaje) || other.mensaje == mensaje));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,usuarioId,reservaId,tipo,leida,createdAt,mensaje);

@override
String toString() {
  return 'Notificacion(id: $id, usuarioId: $usuarioId, reservaId: $reservaId, tipo: $tipo, leida: $leida, createdAt: $createdAt, mensaje: $mensaje)';
}


}

/// @nodoc
abstract mixin class $NotificacionCopyWith<$Res>  {
  factory $NotificacionCopyWith(Notificacion value, $Res Function(Notificacion) _then) = _$NotificacionCopyWithImpl;
@useResult
$Res call({
 int id, int usuarioId, int? reservaId, TipoNotificacion tipo, bool leida, String createdAt, String mensaje
});




}
/// @nodoc
class _$NotificacionCopyWithImpl<$Res>
    implements $NotificacionCopyWith<$Res> {
  _$NotificacionCopyWithImpl(this._self, this._then);

  final Notificacion _self;
  final $Res Function(Notificacion) _then;

/// Create a copy of Notificacion
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? usuarioId = null,Object? reservaId = freezed,Object? tipo = null,Object? leida = null,Object? createdAt = null,Object? mensaje = null,}) {
  return _then(Notificacion(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: null == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int,reservaId: freezed == reservaId ? _self.reservaId : reservaId // ignore: cast_nullable_to_non_nullable
as int?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoNotificacion,leida: null == leida ? _self.leida : leida // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,mensaje: null == mensaje ? _self.mensaje : mensaje // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [Notificacion].
extension NotificacionPatterns on Notificacion {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Notificacion value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Notificacion() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Notificacion value)  $default,){
final _that = this;
switch (_that) {
case _Notificacion():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Notificacion value)?  $default,){
final _that = this;
switch (_that) {
case _Notificacion() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int usuarioId,  int? reservaId,  TipoNotificacion tipo,  bool leida,  String createdAt,  String mensaje)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Notificacion() when $default != null:
return $default(_that.id,_that.usuarioId,_that.reservaId,_that.tipo,_that.leida,_that.createdAt,_that.mensaje);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int usuarioId,  int? reservaId,  TipoNotificacion tipo,  bool leida,  String createdAt,  String mensaje)  $default,) {final _that = this;
switch (_that) {
case _Notificacion():
return $default(_that.id,_that.usuarioId,_that.reservaId,_that.tipo,_that.leida,_that.createdAt,_that.mensaje);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int usuarioId,  int? reservaId,  TipoNotificacion tipo,  bool leida,  String createdAt,  String mensaje)?  $default,) {final _that = this;
switch (_that) {
case _Notificacion() when $default != null:
return $default(_that.id,_that.usuarioId,_that.reservaId,_that.tipo,_that.leida,_that.createdAt,_that.mensaje);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Notificacion implements Notificacion {
  const _Notificacion({required this.id, required this.usuarioId, this.reservaId, required this.tipo, required this.leida, required this.createdAt, required this.mensaje});
  factory _Notificacion.fromJson(Map<String, dynamic> json) => _$NotificacionFromJson(json);

@override final  int id;
@override final  int usuarioId;
@override final  int? reservaId;
@override final  TipoNotificacion tipo;
@override final  bool leida;
@override final  String createdAt;
@override final  String mensaje;

/// Create a copy of Notificacion
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NotificacionCopyWith<_Notificacion> get copyWith => __$NotificacionCopyWithImpl<_Notificacion>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NotificacionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Notificacion&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.reservaId, reservaId) || other.reservaId == reservaId)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.leida, leida) || other.leida == leida)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.mensaje, mensaje) || other.mensaje == mensaje));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,usuarioId,reservaId,tipo,leida,createdAt,mensaje);

@override
String toString() {
  return 'Notificacion(id: $id, usuarioId: $usuarioId, reservaId: $reservaId, tipo: $tipo, leida: $leida, createdAt: $createdAt, mensaje: $mensaje)';
}


}

/// @nodoc
abstract mixin class _$NotificacionCopyWith<$Res> implements $NotificacionCopyWith<$Res> {
  factory _$NotificacionCopyWith(_Notificacion value, $Res Function(_Notificacion) _then) = __$NotificacionCopyWithImpl;
@override @useResult
$Res call({
 int id, int usuarioId, int? reservaId, TipoNotificacion tipo, bool leida, String createdAt, String mensaje
});




}
/// @nodoc
class __$NotificacionCopyWithImpl<$Res>
    implements _$NotificacionCopyWith<$Res> {
  __$NotificacionCopyWithImpl(this._self, this._then);

  final _Notificacion _self;
  final $Res Function(_Notificacion) _then;

/// Create a copy of Notificacion
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? usuarioId = null,Object? reservaId = freezed,Object? tipo = null,Object? leida = null,Object? createdAt = null,Object? mensaje = null,}) {
  return _then(_Notificacion(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: null == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int,reservaId: freezed == reservaId ? _self.reservaId : reservaId // ignore: cast_nullable_to_non_nullable
as int?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoNotificacion,leida: null == leida ? _self.leida : leida // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,mensaje: null == mensaje ? _self.mensaje : mensaje // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
